
import pandas as pd
from sqlalchemy import text

from app.db.connection import engine


def fetch_closing_prices():
    """
    Fetch historical closing prices for all instruments.
    """

    query = text("""
        SELECT
            i.ticker,
            p.price_date,
            p.close_price
        FROM daily_prices p
        JOIN instruments i
            ON p.instrument_id = i.instrument_id
        ORDER BY i.ticker, p.price_date;
    """)

    with engine.connect() as connection:
        df = pd.read_sql(query, connection)

    if df.empty:
        raise ValueError("No historical price data found.")

    df["price_date"] = pd.to_datetime(df["price_date"])
    df["close_price"] = pd.to_numeric(df["close_price"])

    return df


def calculate_daily_returns(prices):
    """
    Calculate daily percentage returns for each stock.

    Formula:
    Return = (Today's Close / Previous Close) - 1
    """

    prices = prices.sort_values(
        ["ticker", "price_date"]
    ).copy()

    prices["daily_return"] = (
        prices.groupby("ticker")["close_price"]
        .pct_change(fill_method=None)
    )

    return prices



def validate_returns(returns):
    """
    Validate the calculated daily returns.
    """

    if returns.empty:
        raise ValueError("Returns dataset is empty.")

    # Check the first chronological observation for each stock
    first_rows = (
        returns.sort_values(["ticker", "price_date"])
        .groupby("ticker", sort=False)
        .head(1)
    )

    if first_rows["daily_return"].notna().any():
        raise ValueError(
            "First observation should have a null return."
        )

    # Check for infinite values
    if returns["daily_return"].isin(
        [float("inf"), float("-inf")]
    ).any():
        raise ValueError("Infinite returns detected.")

    # Check for missing returns after the first observation
    subsequent_rows = (
        returns.sort_values(["ticker", "price_date"])
        .groupby("ticker", sort=False)
        .cumcount() > 0
    )

    if returns.loc[
        subsequent_rows, "daily_return"
    ].isna().any():
        raise ValueError(
            "Missing returns detected after first observation."
        )

    print("Return validation successful.")


def main():

    print("\n==============================")
    print("FINVEST IQ DAILY RETURNS ENGINE")
    print("==============================")

    # Fetch historical prices
    prices = fetch_closing_prices()

    print(f"\nPrice records fetched: {len(prices)}")

    # Calculate returns
    returns = calculate_daily_returns(prices)

    # Validate
    validate_returns(returns)

    # Summary
    print("\nSTOCK SUMMARY")
    print("------------------------------")

    summary = returns.groupby("ticker").agg(
        price_records=("close_price", "count"),
        return_records=("daily_return", "count"),
        average_daily_return=("daily_return", "mean"),
        minimum_daily_return=("daily_return", "min"),
        maximum_daily_return=("daily_return", "max")
    )

    print(summary.to_string())

    print("\nSAMPLE DAILY RETURNS")
    print("------------------------------")

    print(
        returns[
            ["ticker", "price_date", "close_price", "daily_return"]
        ].tail(12).to_string(index=False)
    )

    print("\nDaily returns engine completed.")


if __name__ == "__main__":
    main()
