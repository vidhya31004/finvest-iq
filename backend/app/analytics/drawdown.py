
import pandas as pd

from app.analytics.returns import fetch_closing_prices


def calculate_drawdown(prices):
    """
    Calculate historical drawdown for each stock.

    Drawdown = (Current Price / Previous Peak) - 1
    """

    results = prices.sort_values(
        ["ticker", "price_date"]
    ).copy()

    # Calculate running historical peak for each stock
    results["running_peak"] = (
        results.groupby("ticker")["close_price"]
        .cummax()
    )

    # Calculate drawdown
    results["drawdown"] = (
        results["close_price"] / results["running_peak"]
    ) - 1

    return results


def calculate_drawdown_summary(drawdowns):
    """
    Calculate maximum drawdown and identify peak and trough dates.
    """

    records = []

    for ticker, group in drawdowns.groupby("ticker"):

        group = group.sort_values("price_date").copy()

        # Find maximum drawdown
        trough_index = group["drawdown"].idxmin()

        trough_row = group.loc[trough_index]

        # Find the previous peak before the trough
        peak_candidates = group[
            group["price_date"] <= trough_row["price_date"]
        ]

        peak_row = peak_candidates.loc[
            peak_candidates["close_price"].idxmax()
        ]

        # Find recovery date, if the price subsequently
        # reaches or exceeds the previous peak
        recovery_candidates = group[
            (group["price_date"] > trough_row["price_date"])
            & (group["close_price"] >= peak_row["close_price"])
        ]

        recovery_date = (
            recovery_candidates.iloc[0]["price_date"]
            if not recovery_candidates.empty
            else pd.NaT
        )

        records.append({
            "ticker": ticker,
            "maximum_drawdown": trough_row["drawdown"],
            "peak_date": peak_row["price_date"],
            "peak_price": peak_row["close_price"],
            "trough_date": trough_row["price_date"],
            "trough_price": trough_row["close_price"],
            "recovery_date": recovery_date
        })

    return pd.DataFrame(records).set_index("ticker")


def validate_drawdowns(drawdowns, summary):
    """
    Validate drawdown calculations.
    """

    if drawdowns.empty:
        raise ValueError("Drawdown dataset is empty.")

    if summary.empty:
        raise ValueError("Drawdown summary is empty.")

    if (drawdowns["drawdown"] > 1e-10).any():
        raise ValueError("Positive drawdown detected.")

    if (drawdowns["drawdown"] < -1).any():
        raise ValueError("Drawdown below -100% detected.")

    if (summary["maximum_drawdown"] > 1e-10).any():
        raise ValueError("Maximum drawdown cannot be positive.")

    print("Drawdown validation successful.")


def main():

    print("\n================================")
    print("FINVEST IQ DRAWDOWN ENGINE")
    print("================================")

    # Fetch closing prices
    prices = fetch_closing_prices()

    print(f"\nPrice records fetched: {len(prices)}")

    # Calculate drawdowns
    drawdowns = calculate_drawdown(prices)

    # Generate summary
    summary = calculate_drawdown_summary(drawdowns)

    # Validate
    validate_drawdowns(drawdowns, summary)

    # Display results
    display_summary = summary.copy()

    display_summary["maximum_drawdown"] *= 100

    print("\nMAXIMUM DRAWDOWN SUMMARY")
    print("--------------------------------")

    print(display_summary.round(3).to_string())

    print("\nLATEST DRAWDOWN")
    print("--------------------------------")

    latest = (
        drawdowns.sort_values("price_date")
        .groupby("ticker")
        .tail(1)
        .copy()
    )

    latest["drawdown"] *= 100

    print(
        latest[
            ["ticker", "price_date", "close_price", "running_peak", "drawdown"]
        ].to_string(index=False)
    )

    print("\nDrawdown engine completed.")


if __name__ == "__main__":
    main()
