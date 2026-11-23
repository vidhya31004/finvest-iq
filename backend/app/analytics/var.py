
import pandas as pd

from app.analytics.returns import (
    fetch_closing_prices,
    calculate_daily_returns,
    validate_returns
)


def calculate_historical_var(returns, confidence_level):
    """
    Calculate historical Value at Risk.
    Returns a positive loss percentage.
    """

    valid_returns = returns.dropna()

    if valid_returns.empty:
        raise ValueError("No valid returns available for VaR.")

    if not 0 < confidence_level < 1:
        raise ValueError("Confidence level must be between 0 and 1.")

    loss_quantile = valid_returns.quantile(1 - confidence_level)

    return max(0.0, -float(loss_quantile))


def calculate_historical_cvar(returns, confidence_level):
    """
    Calculate historical Conditional Value at Risk.
    """

    valid_returns = returns.dropna()

    if valid_returns.empty:
        raise ValueError("No valid returns available for CVaR.")

    if not 0 < confidence_level < 1:
        raise ValueError("Confidence level must be between 0 and 1.")

    loss_quantile = valid_returns.quantile(1 - confidence_level)

    tail_returns = valid_returns[
        valid_returns <= loss_quantile
    ]

    if tail_returns.empty:
        return 0.0

    return max(0.0, -float(tail_returns.mean()))


def calculate_var_summary(returns):
    """
    Calculate 95% and 99% VaR and CVaR for each stock.
    """

    records = []

    for ticker, group in returns.groupby("ticker"):

        daily_returns = group["daily_return"].dropna()

        records.append({
            "ticker": ticker,
            "observations": len(daily_returns),

            "VaR_95": calculate_historical_var(
                daily_returns, 0.95
            ),

            "VaR_99": calculate_historical_var(
                daily_returns, 0.99
            ),

            "CVaR_95": calculate_historical_cvar(
                daily_returns, 0.95
            ),

            "CVaR_99": calculate_historical_cvar(
                daily_returns, 0.99
            )
        })

    return pd.DataFrame(records).set_index("ticker")


def validate_var_summary(summary):
    """
    Validate VaR and CVaR calculations.
    """

    risk_columns = [
        "VaR_95",
        "VaR_99",
        "CVaR_95",
        "CVaR_99"
    ]

    if summary.empty:
        raise ValueError("VaR summary is empty.")

    if summary[risk_columns].isnull().any().any():
        raise ValueError("Missing VaR or CVaR values detected.")

    if (summary[risk_columns] < 0).any().any():
        raise ValueError("Negative loss values detected.")

    if (summary["VaR_99"] < summary["VaR_95"]).any():
        raise ValueError("99% VaR should be at least 95% VaR.")

    if (summary["CVaR_99"] < summary["CVaR_95"]).any():
        raise ValueError("99% CVaR should be at least 95% CVaR.")

    if (
        summary["CVaR_95"] < summary["VaR_95"] - 1e-10
    ).any():
        raise ValueError("95% CVaR should be at least 95% VaR.")

    if (
        summary["CVaR_99"] < summary["VaR_99"] - 1e-10
    ).any():
        raise ValueError("99% CVaR should be at least 99% VaR.")

    print("VaR and CVaR validation successful.")


def main():

    print("\n================================")
    print("FINVEST IQ HISTORICAL VAR ENGINE")
    print("================================")

    # Fetch historical prices
    prices = fetch_closing_prices()

    print(f"\nPrice records fetched: {len(prices)}")

    # Calculate daily returns
    returns = calculate_daily_returns(prices)

    # Validate returns
    validate_returns(returns)

    # Calculate VaR and CVaR
    summary = calculate_var_summary(returns)

    # Validate risk metrics
    validate_var_summary(summary)

    # Convert risk values to percentages.
    # Keep observation counts unchanged.
    display_summary = summary.copy()

    risk_columns = [
        "VaR_95",
        "VaR_99",
        "CVaR_95",
        "CVaR_99"
    ]

    display_summary[risk_columns] = (
        display_summary[risk_columns] * 100
    )

    print("\nHISTORICAL VAR AND CVAR SUMMARY")
    print("--------------------------------")

    print(display_summary.round(3).to_string())

    print("\nNote: VaR and CVaR values are displayed as percentages.")

    print("\nVaR engine completed.")


if __name__ == "__main__":
    main()
