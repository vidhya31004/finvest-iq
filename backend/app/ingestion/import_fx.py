
from pathlib import Path

import pandas as pd
from sqlalchemy import text

from app.db.connection import engine


PROJECT_ROOT = Path(__file__).resolve().parents[3]

FX_FILE = PROJECT_ROOT / "data" / "raw" / "fx" / "USD_INR_ECB.csv"

SOURCE_NAME = "Frankfurter FX"

EXPECTED_BASE = "USD"
EXPECTED_QUOTE = "INR"


def load_fx_data():

    if not FX_FILE.exists():
        raise FileNotFoundError(f"FX file not found: {FX_FILE}")

    data = pd.read_csv(FX_FILE)

    required_columns = ["date", "base", "quote", "rate"]

    if not all(column in data.columns for column in required_columns):
        raise ValueError("FX CSV is missing required columns.")

    return data


def validate_fx_data(data):

    if data.empty:
        raise ValueError("FX dataset is empty.")

    data = data.copy()

    data["date"] = pd.to_datetime(
        data["date"], errors="coerce"
    )

    data["rate"] = pd.to_numeric(
        data["rate"], errors="coerce"
    )

    if data[["date", "rate", "base", "quote"]].isnull().any().any():
        raise ValueError("FX data contains missing or invalid values.")

    if not (data["base"] == EXPECTED_BASE).all():
        raise ValueError("Unexpected base currency.")

    if not (data["quote"] == EXPECTED_QUOTE).all():
        raise ValueError("Unexpected quote currency.")

    if (data["rate"] <= 0).any():
        raise ValueError("Exchange rates must be positive.")

    if data["date"].duplicated().any():
        raise ValueError("Duplicate FX dates detected.")

    if not data["date"].is_monotonic_increasing:
        raise ValueError("FX dates must be in ascending order.")

    if (data["date"].dt.day_of_week >= 5).any():
        raise ValueError("Weekend FX observations detected.")

    print("FX data validation successful.")

    return data



def import_fx_data(data):

    with engine.begin() as connection:

        source_id = connection.execute(
            text("""
                SELECT source_id
                FROM data_sources
                WHERE source_name = :source_name
                  AND source_type = 'FX'
            """),
            {"source_name": SOURCE_NAME}
        ).scalar_one_or_none()

        if source_id is None:
            source_id = connection.execute(
                text("""
                    INSERT INTO data_sources (
                        source_name,
                        source_type
                    )
                    VALUES (:source_name, 'FX')
                    RETURNING source_id
                """),
                {"source_name": SOURCE_NAME}
            ).scalar_one()

        records = []

        for _, row in data.iterrows():
            records.append({
                "base_currency": EXPECTED_BASE,
                "quote_currency": EXPECTED_QUOTE,
                "rate_date": row["date"].date(),
                "exchange_rate": float(row["rate"]),
                "source_id": source_id
            })

        connection.execute(
            text("""
                INSERT INTO fx_rates (
                    base_currency,
                    quote_currency,
                    rate_date,
                    exchange_rate,
                    source_id
                )
                VALUES (
                    :base_currency,
                    :quote_currency,
                    :rate_date,
                    :exchange_rate,
                    :source_id
                )
                ON CONFLICT (
                    base_currency,
                    quote_currency,
                    rate_date
                )
                DO UPDATE SET
                    exchange_rate = EXCLUDED.exchange_rate,
                    source_id = EXCLUDED.source_id
            """),
            records
        )

    print(f"FX records processed: {len(records)}")


def main():

    print("\n================================")
    print("FINVEST IQ FX INGESTION ENGINE")
    print("================================")

    data = load_fx_data()

    print(f"\nRecords loaded: {len(data)}")

    data = validate_fx_data(data)

    import_fx_data(data)

    print("\nFX ingestion completed successfully.")


if __name__ == "__main__":
    main()
