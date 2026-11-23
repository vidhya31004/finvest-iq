
import pandas as pd
from sqlalchemy import text

from app.db.connection import engine


PORTFOLIO_ID = 1
TRADING_DAYS = 252


def fetch_portfolio_data():

    with engine.connect() as connection:

        portfolio = pd.read_sql(
            text("""
                SELECT portfolio_id, portfolio_name, base_currency
                FROM portfolios
                WHERE portfolio_id = :portfolio_id
            """),
            connection,
            params={"portfolio_id": PORTFOLIO_ID}
        )

        if portfolio.empty:
            raise ValueError("Portfolio not found.")

        if portfolio.iloc[0]["base_currency"] != "USD":
            raise ValueError("This version supports USD portfolios only.")

        holdings = pd.read_sql(
            text("""
                SELECT
                    i.ticker,
                    i.currency,
                    h.quantity,
                    h.average_cost
                FROM portfolio_holdings h
                JOIN instruments i
                    ON h.instrument_id = i.instrument_id
                WHERE h.portfolio_id = :portfolio_id
                ORDER BY i.ticker
            """),
            connection,
            params={"portfolio_id": PORTFOLIO_ID}
        )

        prices = pd.read_sql(
            text("""
                SELECT
                    i.ticker,
                    p.price_date,
                    p.close_price
                FROM daily_prices p
                JOIN instruments i
                    ON p.instrument_id = i.instrument_id
                JOIN portfolio_holdings h
                    ON h.instrument_id = i.instrument_id
                WHERE h.portfolio_id = :portfolio_id
                ORDER BY i.ticker, p.price_date
            """),
            connection,
            params={"portfolio_id": PORTFOLIO_ID}
        )

        fx_rates = pd.read_sql(
            text("""
                SELECT rate_date, exchange_rate
                FROM fx_rates
                WHERE base_currency = 'USD'
                  AND quote_currency = 'INR'
                ORDER BY rate_date
            """),
            connection
        )

    if holdings.empty or prices.empty or fx_rates.empty:
        raise ValueError("Portfolio holdings, prices or FX data are missing.")

    return portfolio.iloc[0], holdings, prices, fx_rates


def calculate_usd_prices(holdings, prices, fx_rates):

    prices = prices.copy()
    fx_rates = fx_rates.copy()

    prices["price_date"] = pd.to_datetime(prices["price_date"])
    fx_rates["rate_date"] = pd.to_datetime(fx_rates["rate_date"])

    fx_rates = fx_rates.sort_values("rate_date")

    converted_data = []

    for _, holding in holdings.iterrows():

        ticker = holding["ticker"]
        currency = holding["currency"]

        stock = prices[
            prices["ticker"] == ticker
        ].copy()

        stock = stock.sort_values("price_date")

        if currency == "USD":

            stock["exchange_rate"] = 1.0

        elif currency == "INR":

            stock = pd.merge_asof(
                stock,
                fx_rates,
                left_on="price_date",
                right_on="rate_date",
                direction="backward",
                tolerance=pd.Timedelta(days=5)
            )

            stock["exchange_rate"] = stock["exchange_rate"]

            if stock["exchange_rate"].isna().any():
                raise ValueError(
                    f"Missing valid FX rate for {ticker}."
                )

        else:
            raise ValueError(
                f"Unsupported currency {currency} for {ticker}."
            )

        stock["usd_price"] = (
            stock["close_price"] / stock["exchange_rate"]
        )

        stock["quantity"] = float(holding["quantity"])

        stock["usd_market_value"] = (
            stock["usd_price"] * stock["quantity"]
        )

        converted_data.append(
            stock[
                [
                    "ticker",
                    "price_date",
                    "usd_price",
                    "usd_market_value",
                    "exchange_rate"
                ]
            ]
        )

    return pd.concat(converted_data, ignore_index=True)


def calculate_portfolio_values(converted_prices):

    market_values = converted_prices.pivot(
        index="price_date",
        columns="ticker",
        values="usd_market_value"
    )

    # Use only dates with prices for every portfolio holding.
    market_values = market_values.dropna()

    if market_values.empty:
        raise ValueError(
            "No common valuation dates across all portfolio holdings."
        )

    portfolio_values = market_values.sum(axis=1)

    portfolio_returns = portfolio_values.pct_change(
        fill_method=None
    ).dropna()

    return market_values, portfolio_values, portfolio_returns


def calculate_portfolio_summary(
    holdings,
    market_values,
    portfolio_values,
    portfolio_returns
):

    latest_values = market_values.iloc[-1]

    total_value = float(portfolio_values.iloc[-1])

    if total_value <= 0:
        raise ValueError("Portfolio value must be positive.")

    allocation = pd.DataFrame({
        "ticker": latest_values.index,
        "market_value_usd": latest_values.values
    })

    allocation["weight_pct"] = (
        allocation["market_value_usd"] / total_value * 100
    )

    allocation = allocation.merge(
        holdings[["ticker", "currency", "quantity", "average_cost"]],
        on="ticker",
        how="left"
    )

    daily_volatility = portfolio_returns.std()

    annualised_volatility = (
        daily_volatility * (TRADING_DAYS ** 0.5)
    )

    quantile_95 = portfolio_returns.quantile(0.05)
    quantile_99 = portfolio_returns.quantile(0.01)

    var_95 = max(0.0, -float(quantile_95))
    var_99 = max(0.0, -float(quantile_99))

    cvar_95 = max(
        0.0,
        -float(portfolio_returns[portfolio_returns <= quantile_95].mean())
    )

    cvar_99 = max(
        0.0,
        -float(portfolio_returns[portfolio_returns <= quantile_99].mean())
    )

    risk_summary = {
        "portfolio_value_usd": total_value,
        "daily_volatility_pct": float(daily_volatility * 100),
        "annualised_volatility_pct": float(
            annualised_volatility * 100
        ),
        "var_95_pct": var_95 * 100,
        "var_99_pct": var_99 * 100,
        "cvar_95_pct": cvar_95 * 100,
        "cvar_99_pct": cvar_99 * 100,
        "observations": len(portfolio_returns)
    }

    return allocation, risk_summary


def validate_portfolio_results(
    market_values,
    portfolio_values,
    portfolio_returns,
    allocation,
    risk_summary
):

    if market_values.empty or portfolio_returns.empty:
        raise ValueError("Portfolio analytics returned no observations.")

    if not market_values.map(
        lambda value: pd.notna(value) and value > 0
    ).all().all():
        raise ValueError("Invalid portfolio market values.")

    if not portfolio_returns.map(
        lambda value: pd.notna(value) and pd.notna(value)
    ).all():
        raise ValueError("Invalid portfolio returns.")

    if not abs(allocation["weight_pct"].sum() - 100) < 1e-6:
        raise ValueError("Portfolio weights do not sum to 100%.")

    if risk_summary["var_99_pct"] + 1e-10 < risk_summary["var_95_pct"]:
        raise ValueError("99% VaR must be at least 95% VaR.")

    if risk_summary["cvar_99_pct"] + 1e-10 < risk_summary["cvar_95_pct"]:
        raise ValueError("99% CVaR must be at least 95% CVaR.")

    print("Portfolio risk validation successful.")


def main():

    print("\n================================")
    print("FINVEST IQ PORTFOLIO RISK ENGINE")
    print("================================")

    portfolio, holdings, prices, fx_rates = fetch_portfolio_data()

    print(f"\nPortfolio: {portfolio['portfolio_name']}")
    print(f"Base currency: {portfolio['base_currency']}")
    print(f"Number of holdings: {len(holdings)}")

    converted_prices = calculate_usd_prices(
        holdings,
        prices,
        fx_rates
    )

    market_values, portfolio_values, portfolio_returns = (
        calculate_portfolio_values(converted_prices)
    )

    allocation, risk_summary = calculate_portfolio_summary(
        holdings,
        market_values,
        portfolio_values,
        portfolio_returns
    )

    validate_portfolio_results(
        market_values,
        portfolio_values,
        portfolio_returns,
        allocation,
        risk_summary
    )

    print("\nPORTFOLIO ALLOCATION")
    print("--------------------------------")
    print(
        allocation[
            ["ticker", "currency", "quantity", "market_value_usd", "weight_pct"]
        ].round(3).to_string(index=False)
    )

    print("\nPORTFOLIO RISK SUMMARY")
    print("--------------------------------")

    for metric, value in risk_summary.items():
        if metric == "observations":
            print(f"{metric}: {value}")
        else:
            print(f"{metric}: {value:.3f}")

    print("\nPORTFOLIO VALUE HISTORY")
    print("--------------------------------")
    print(f"First valuation: {portfolio_values.index.min().date()}")
    print(f"Latest valuation: {portfolio_values.index.max().date()}")

    print("\nPortfolio risk engine completed.")


if __name__ == "__main__":
    main()
