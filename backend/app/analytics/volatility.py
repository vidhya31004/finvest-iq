
import pandas as pd

from app.analytics.returns import (
    fetch_closing_prices,
    calculate_daily_returns,
    validate_returns
)


TRADING_DAYS = 252


def calculate_volatility(returns):
    """
    Calculate rolling and annualised historical volatility.

    20-day volatility: Short-term risk
    60-day volatility: Medium-term risk
    Annualised volatility: Daily standard deviation * sqrt(252)
    """

    results = returns.copy()

    results = results.sort_values(
        ["ticker", "price_date"]
    )

    grouped_returns = results.groupby("ticker")["daily_return"]

    # Rolling daily volatility
    results["volatility_20d"] = grouped_returns.transform(
        lambda series: series.rolling(
            window=20,
            min_periods=20
        ).std()
    )

    results["volatility_60d"] = grouped_returns.transform(
        lambda series: series.rolling(
            window=60,
            min_periods=60
        ).std()
    )

    # Annualised rolling volatility
    results["annualised_volatility_20d"] = (
        results["volatility_20d"] * (TRADING_DAYS ** 0.5)
    )

    results["annualised_volatility_60d"] = (
        results["volatility_60d"] * (TRADING_DAYS ** 0.5)
    )

    return results


def create_volatility_summary(volatility):
    """
    Create a summary of volatility metrics for each stock.
    """

    summary = volatility.groupby("ticker").agg(
        average_daily_volatility=("daily_return", "std"),
        average_20d_volatility=("volatility_20d", "mean"),
        average_60d_volatility=("volatility_60d", "mean"),
        latest_20d_volatility=("volatility_20d", "last"),
        latest_60d_volatility=("volatility_60d", "last"),
        latest_annualised_20d=("annualised_volatility_20d", "last"),
        latest_annualised_60d=("annualised_volatility_60d", "last")
    )

    # Annualised full-period volatility
    summary["annualised_full_period_volatility"] = (
        summary["average_daily_volatility"] * (TRADING_DAYS ** 0.5)
    )

    return summary


def validate_volatility(volatility):
    """
    Validate calculated volatility values.
    """

    volatility_columns = [
        "volatility_20d",
        "volatility_60d",
        "annualised_volatility_20d",
        "annualised_volatility_60d"
    ]

    for column in volatility_columns:

        valid_values = volatility[column].dropna()

        if (valid_values < 0).any():
            raise ValueError(
                f"Negative volatility detected in {column}"
            )

        if not valid_values.map(
            lambda value: pd.notna(value) and abs(value) != float("inf")
        ).all():
            raise ValueError(
                f"Invalid volatility detected in {column}"
            )

    print("Volatility validation successful.")


def main():

    print("\n================================")
    print("FINVEST IQ VOLATILITY ENGINE")
    print("================================")

    # Fetch historical prices
    prices = fetch_closing_prices()

    # Calculate daily returns
    returns = calculate_daily_returns(prices)

    # Validate returns
    validate_returns(returns)

    # Calculate volatility
    volatility = calculate_volatility(returns)

    # Validate volatility
    validate_volatility(volatility)

    # Generate summary
    summary = create_volatility_summary(volatility)

    print("\nVOLATILITY SUMMARY")
    print("--------------------------------")

    print(summary.to_string())

    print("\nLATEST STOCK VOLATILITY")
    print("--------------------------------")

    latest = (
        volatility.sort_values("price_date")
        .groupby("ticker")
        .tail(1)
    )

    print(
        latest[
            [
                "ticker",
                "price_date",
                "volatility_20d",
                "volatility_60d",
                "annualised_volatility_20d",
                "annualised_volatility_60d"
            ]
        ].to_string(index=False)
    )

    print("\nVolatility engine completed.")


if __name__ == "__main__":
    main()
