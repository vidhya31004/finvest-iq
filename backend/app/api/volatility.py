
import pandas as pd
from fastapi import APIRouter, HTTPException

from app.analytics.returns import (
    fetch_closing_prices,
    calculate_daily_returns,
    validate_returns,
)

from app.analytics.volatility import (
    calculate_volatility,
    create_volatility_summary,
    validate_volatility,
)

router = APIRouter(prefix="/api/volatility", tags=["Volatility"])


def safe_float(value):
    """Convert a numeric value to a JSON-safe float."""
    if pd.isna(value):
        return None

    result = float(value)

    if not pd.notna(result) or result == float("inf") or result == float("-inf"):
        return None

    return result


@router.get("/stocks")
def get_stock_volatility():
    try:
        # Load prices and calculate daily returns
        prices = fetch_closing_prices()
        returns = calculate_daily_returns(prices)
        validate_returns(returns)

        # Calculate rolling volatility
        volatility = calculate_volatility(returns)
        validate_volatility(volatility)

        # Generate summary statistics
        summary = create_volatility_summary(volatility)

        stocks = []

        for ticker in summary.index:
            ticker_history = volatility[
                volatility["ticker"] == ticker
            ].sort_values("price_date")

            latest = ticker_history.iloc[-1]
            stats = summary.loc[ticker]

            stocks.append({
                "ticker": ticker,
                "average_daily_volatility": safe_float(
                    stats["average_daily_volatility"]
                ),
                "average_20d_volatility": safe_float(
                    stats["average_20d_volatility"]
                ),
                "average_60d_volatility": safe_float(
                    stats["average_60d_volatility"]
                ),
                "latest_20d_volatility": safe_float(
                    latest["volatility_20d"]
                ),
                "latest_60d_volatility": safe_float(
                    latest["volatility_60d"]
                ),
                "latest_annualised_20d": safe_float(
                    latest["annualised_volatility_20d"]
                ),
                "latest_annualised_60d": safe_float(
                    latest["annualised_volatility_60d"]
                ),
                "annualised_full_period_volatility": safe_float(
                    stats["annualised_full_period_volatility"]
                ),
                "latest_date": latest["price_date"].strftime("%Y-%m-%d"),
            })

        history = []

        for row in volatility.itertuples(index=False):
            history.append({
                "ticker": row.ticker,
                "date": row.price_date.strftime("%Y-%m-%d"),
                "volatility_20d": safe_float(row.volatility_20d),
                "volatility_60d": safe_float(row.volatility_60d),
                "annualised_volatility_20d": safe_float(
                    row.annualised_volatility_20d
                ),
                "annualised_volatility_60d": safe_float(
                    row.annualised_volatility_60d
                ),
            })

        return {
            "stocks": stocks,
            "history": history,
            "total_stocks": len(stocks),
            "observations": len(history),
            "methodology": {
                "rolling_windows": [20, 60],
                "annualisation_factor": 252,
                "formula": "Rolling standard deviation of daily returns multiplied by sqrt(252)",
            },
        }

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=f"Unable to calculate stock volatility: {str(error)}",
        )
