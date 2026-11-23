
from fastapi import APIRouter, HTTPException
from sqlalchemy import text

from app.db.connection import engine

router = APIRouter(prefix="/api/portfolio", tags=["Portfolio"])


@router.get("/{portfolio_id}/performance")
def get_portfolio_performance(portfolio_id: int):
    """
    Return historical portfolio market values in the
    portfolio's base currency.

    INR assets are converted into USD using the latest
    available USD/INR rate on or before each price date.
    """

    query = text("""
        WITH holding_prices AS (
            SELECT
                p.price_date,
                i.ticker,
                i.currency,
                h.quantity,
                p.close_price,
                CASE
                    WHEN i.currency = 'USD'
                        THEN p.close_price
                    WHEN i.currency = 'INR'
                        THEN p.close_price / fx.exchange_rate
                    ELSE NULL
                END AS price_in_usd

            FROM portfolio_holdings h

            JOIN instruments i
                ON h.instrument_id = i.instrument_id

            JOIN daily_prices p
                ON p.instrument_id = i.instrument_id

            JOIN portfolios pf
                ON pf.portfolio_id = h.portfolio_id

            LEFT JOIN LATERAL (
                SELECT exchange_rate
                FROM fx_rates f
                WHERE f.base_currency = 'USD'
                  AND f.quote_currency = 'INR'
                  AND f.rate_date <= p.price_date
                ORDER BY f.rate_date DESC
                LIMIT 1
            ) fx ON i.currency = 'INR'

            WHERE h.portfolio_id = :portfolio_id
              AND (
                  i.currency = 'USD'
                  OR (
                      i.currency = 'INR'
                      AND fx.exchange_rate IS NOT NULL
                  )
              )
        ),

        daily_portfolio_values AS (
            SELECT
                price_date,
                SUM(quantity * price_in_usd) AS portfolio_value_usd,
                COUNT(DISTINCT ticker) AS available_holdings
            FROM holding_prices
            GROUP BY price_date
        )

        SELECT
            price_date,
            portfolio_value_usd,
            available_holdings
        FROM daily_portfolio_values
        WHERE available_holdings = (
            SELECT COUNT(*)
            FROM portfolio_holdings
            WHERE portfolio_id = :portfolio_id
        )
        ORDER BY price_date
    """)

    try:
        with engine.connect() as connection:
            portfolio = connection.execute(
                text("""
                    SELECT portfolio_id, portfolio_name, base_currency
                    FROM portfolios
                    WHERE portfolio_id = :portfolio_id
                """),
                {"portfolio_id": portfolio_id},
            ).mappings().first()

            if not portfolio:
                raise HTTPException(
                    status_code=404,
                    detail="Portfolio not found",
                )

            if portfolio["base_currency"].strip() != "USD":
                raise HTTPException(
                    status_code=400,
                    detail="This endpoint currently supports USD portfolios only",
                )

            rows = connection.execute(
                query,
                {"portfolio_id": portfolio_id},
            ).mappings().all()

        if not rows:
            raise HTTPException(
                status_code=404,
                detail="No complete portfolio valuation history found",
            )

        return {
            "portfolio_id": portfolio["portfolio_id"],
            "portfolio_name": portfolio["portfolio_name"],
            "base_currency": "USD",
            "observations": len(rows),
            "performance": [
                {
                    "date": row["price_date"].isoformat(),
                    "portfolio_value": round(
                        float(row["portfolio_value_usd"]), 2
                    ),
                    "available_holdings": row["available_holdings"],
                }
                for row in rows
            ],
        }

    except HTTPException:
        raise
    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail="Unable to retrieve portfolio performance",
        ) from error
