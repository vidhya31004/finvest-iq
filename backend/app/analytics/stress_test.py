
import pandas as pd

from app.analytics.portfolio_risk import (
    fetch_portfolio_data,
    calculate_usd_prices
)


def define_stress_scenarios():

    return {
        "US Market Crash": {
            "USD": -0.10,
            "INR": 0.00,
            "FX": 0.00
        },
        "India Market Crash": {
            "USD": 0.00,
            "INR": -0.15,
            "FX": 0.00
        },
        "Global Market Crash": {
            "USD": -0.10,
            "INR": -0.15,
            "FX": 0.00
        },
        "INR Depreciation": {
            "USD": 0.00,
            "INR": 0.00,
            "FX": -0.05
        },
        "Combined Crisis": {
            "USD": -0.20,
            "INR": -0.25,
            "FX": -0.05
        }
    }


def calculate_current_allocation(
    holdings,
    prices,
    fx_rates
):

    # Convert all stock prices into USD
    converted_prices = calculate_usd_prices(
        holdings,
        prices,
        fx_rates
    )

    # Create a date-by-stock market value matrix
    market_values = converted_prices.pivot(
        index="price_date",
        columns="ticker",
        values="usd_market_value"
    )

    # Retain only dates where every holding has a valuation
    market_values = market_values.dropna()

    if market_values.empty:
        raise ValueError(
            "No common valuation dates across all holdings."
        )

    # Select the latest common valuation date
    latest_date = market_values.index.max()

    latest = converted_prices[
        converted_prices["price_date"] == latest_date
    ].copy()

    if latest["ticker"].nunique() != len(holdings):
        raise ValueError(
            "Not all holdings have a valid price "
            "on the common valuation date."
        )

    # Calculate total portfolio value
    total_value = latest["usd_market_value"].sum()

    if total_value <= 0:
        raise ValueError(
            "Portfolio value must be positive."
        )

    # Calculate portfolio weights
    latest["weight"] = (
        latest["usd_market_value"] / total_value
    )

    print(f"Common valuation date: {latest_date.date()}")

    return latest, total_value


def calculate_stress_results(
    allocation,
    total_value,
    scenarios,
    holdings
):

    results = []

    for scenario_name, shocks in scenarios.items():

        scenario_value = 0.0

        for _, holding in allocation.iterrows():

            ticker = holding["ticker"]

            currency = holdings.loc[
                holdings["ticker"] == ticker,
                "currency"
            ].iloc[0]

            if currency == "USD":

                stock_shock = shocks["USD"]
                fx_shock = 0.0

            elif currency == "INR":

                stock_shock = shocks["INR"]
                fx_shock = shocks["FX"]

            else:
                raise ValueError(
                    f"Unsupported currency: {currency}"
                )

            # Apply stock and FX shocks
            if currency == "INR":
               stressed_value = (
                    holding["usd_market_value"]
                    * (1 + stock_shock)
                    / (1 - fx_shock)
             )
            else:
                stressed_value = (
                    holding["usd_market_value"]
                    * (1 + stock_shock)
            )

            scenario_value += stressed_value

        # Calculate portfolio loss
        loss = total_value - scenario_value

        loss_pct = (
            loss / total_value
        ) * 100

        results.append({
            "scenario": scenario_name,
            "portfolio_value_usd": scenario_value,
            "loss_usd": loss,
            "loss_pct": loss_pct
        })

    return pd.DataFrame(results)


def validate_stress_results(
    results,
    total_value
):

    if results.empty:
        raise ValueError(
            "Stress test results are empty."
        )

    if results.isnull().any().any():
        raise ValueError(
            "Stress results contain missing values."
        )

    if not results["portfolio_value_usd"].map(
        lambda value: pd.notna(value) and value >= 0
    ).all():
        raise ValueError(
            "Invalid stressed portfolio value."
        )

    if (
        results["portfolio_value_usd"] > total_value
    ).any():
        raise ValueError(
            "Unexpected stressed portfolio value."
        )

    print("Stress test validation successful.")


def main():

    print("\n================================")
    print("FINVEST IQ STRESS TEST ENGINE")
    print("================================")

    # Fetch portfolio, holdings, prices and FX rates
    portfolio, holdings, prices, fx_rates = (
        fetch_portfolio_data()
    )

    print(f"\nPortfolio: {portfolio['portfolio_name']}")
    print(f"Base currency: {portfolio['base_currency']}")
    print(f"Number of holdings: {len(holdings)}")

    # Calculate latest common-date allocation
    allocation, total_value = calculate_current_allocation(
        holdings,
        prices,
        fx_rates
    )

    print(
        f"\nCurrent portfolio value: "
        f"${total_value:,.2f}"
    )

    # Define stress scenarios
    scenarios = define_stress_scenarios()

    # Calculate stress results
    results = calculate_stress_results(
        allocation,
        total_value,
        scenarios,
        holdings
    )

    # Validate results
    validate_stress_results(
        results,
        total_value
    )

    print("\nCURRENT PORTFOLIO ALLOCATION")
    print("--------------------------------")

    print(
        allocation[
            [
                "ticker",
                "usd_market_value",
                "weight"
            ]
        ].to_string(index=False)
    )

    print("\nSTRESS TEST RESULTS")
    print("--------------------------------")

    print(
        results.round(2).to_string(index=False)
    )

    print("\nStress testing completed.")


if __name__ == "__main__":
    main()
