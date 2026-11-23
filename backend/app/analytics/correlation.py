
import pandas as pd

from app.analytics.returns import (
    fetch_closing_prices,
    calculate_daily_returns,
    validate_returns
)


def calculate_correlation_matrix(returns):
    """
    Calculate pairwise Pearson correlation between stock returns.
    """

    returns = returns.dropna(subset=["daily_return"])

    return returns.pivot(
        index="price_date",
        columns="ticker",
        values="daily_return"
    ).corr(method="pearson", min_periods=30)


def validate_correlation_matrix(correlation):
    """
    Validate correlation matrix values and structure.
    """

    if correlation.empty:
        raise ValueError("Correlation matrix is empty.")

    if correlation.isnull().any().any():
        raise ValueError("Correlation matrix contains missing values.")

    if (correlation < -1).any().any() or (correlation > 1).any().any():
        raise ValueError("Correlation values must be between -1 and +1.")

    if not correlation.equals(correlation.T):
        raise ValueError("Correlation matrix is not symmetrical.")

    if not all(
        abs(correlation.loc[ticker, ticker] - 1) < 1e-10
        for ticker in correlation.index
    ):
        raise ValueError("Diagonal correlation values must equal 1.")

    print("Correlation validation successful.")


def main():

    print("\n================================")
    print("FINVEST IQ CORRELATION ENGINE")
    print("================================")

    # Fetch closing prices
    prices = fetch_closing_prices()

    print(f"\nPrice records fetched: {len(prices)}")

    # Calculate daily returns
    returns = calculate_daily_returns(prices)

    validate_returns(returns)

    # Calculate correlation matrix
    correlation = calculate_correlation_matrix(returns)

    # Validate results
    validate_correlation_matrix(correlation)

    print("\nDAILY RETURN CORRELATION MATRIX")
    print("--------------------------------")

    print(correlation.round(3).to_string())

    print("\nCORRELATION INTERPRETATION")
    print("--------------------------------")

    for i, ticker_1 in enumerate(correlation.columns):

        for ticker_2 in correlation.columns[i + 1:]:

            value = correlation.loc[ticker_1, ticker_2]

            if value >= 0.70:
                interpretation = "Strong positive relationship"

            elif value >= 0.30:
                interpretation = "Moderate positive relationship"

            elif value > -0.30:
                interpretation = "Weak relationship"

            elif value > -0.70:
                interpretation = "Moderate negative relationship"

            else:
                interpretation = "Strong negative relationship"

            print(
                f"{ticker_1} vs {ticker_2}: "
                f"{value:.3f} - {interpretation}"
            )

    print("\nCorrelation engine completed.")


if __name__ == "__main__":
    main()
