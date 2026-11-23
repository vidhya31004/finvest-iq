
from pathlib import Path
import sys

import pandas as pd
from sqlalchemy import text

# --------------------------------------------------
# PROJECT CONFIGURATION
# --------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[3]
BACKEND_PATH = PROJECT_ROOT / "backend"

if str(BACKEND_PATH) not in sys.path:
    sys.path.insert(0, str(BACKEND_PATH))

from app.db.connection import engine

PRICE_FOLDER = PROJECT_ROOT / "data" / "raw" / "prices"

SOURCE_NAMES = {
    "NSE": "NSE India",
    "US_CSV": "US Market CSV"
}


# --------------------------------------------------
# LOAD AND NORMALIZE CSV
# --------------------------------------------------

def load_csv(csv_file):

    df = pd.read_csv(csv_file, thousands=",")

    # NSE INDIA FORMAT
    if "DATE" in df.columns:

        if "SERIES" in df.columns:
            df = df[df["SERIES"] == "EQ"].copy()

        df = df.rename(columns={
            "DATE": "Date",
            "OPEN": "Open",
            "HIGH": "High",
            "LOW": "Low",
            "CLOSE": "Close",
            "VOLUME": "Volume"
        })

        df["Date"] = pd.to_datetime(
            df["Date"],
            format="%d-%b-%Y",
            errors="coerce"
        )

        df["Adj Close"] = None
        source_type = "NSE"

    # US MARKET CSV FORMAT
    else:

        df = df.rename(columns={
            "Close/Last": "Close"
        })

        required = [
            "Date", "Open", "High",
            "Low", "Close", "Volume"
        ]

        missing = [
            col for col in required
            if col not in df.columns
        ]

        if missing:
            raise ValueError(
                f"Missing US CSV columns: {missing}"
            )

        # US dates: MM/DD/YYYY
        df["Date"] = pd.to_datetime(
            df["Date"],
            format="%m/%d/%Y",
            errors="coerce"
        )

        df["Adj Close"] = None
        source_type = "US_CSV"

    # Clean currency symbols and separators
    for column in ["Open", "High", "Low", "Close"]:
        df[column] = (
            df[column]
            .astype(str)
            .str.replace("$", "", regex=False)
            .str.replace(",", "", regex=False)
            .str.strip()
        )

    return df, source_type


# --------------------------------------------------
# VALIDATE PRICE DATA
# --------------------------------------------------

def validate_data(df, ticker):

    required_columns = [
        "Date", "Open", "High",
        "Low", "Close", "Volume"
    ]

    for column in required_columns:
        if column not in df.columns:
            raise ValueError(
                f"{ticker}: Missing column {column}"
            )

    numeric_columns = [
        "Open", "High", "Low",
        "Close", "Volume"
    ]

    for column in numeric_columns:
        df[column] = pd.to_numeric(
            df[column],
            errors="coerce"
        )

    if df[required_columns].isnull().any().any():
        raise ValueError(
            f"{ticker}: Missing or invalid values found"
        )

    # Date ordering
    if not (
        df["Date"].is_monotonic_increasing
        or df["Date"].is_monotonic_decreasing
    ):
        raise ValueError(
            f"{ticker}: Dates are not consistently ordered"
        )

    # Duplicate dates
    if df["Date"].duplicated().any():

        duplicates = (
            df.loc[
                df["Date"].duplicated(keep=False),
                "Date"
            ]
            .dt.strftime("%Y-%m-%d")
            .unique()
            .tolist()
        )

        raise ValueError(
            f"{ticker}: Duplicate dates found: {duplicates}"
        )

    # Positive prices
    if (df[["Open", "High", "Low", "Close"]] <= 0).any().any():
        raise ValueError(
            f"{ticker}: Non-positive prices found"
        )

    # Non-negative volume
    if (df["Volume"] < 0).any():
        raise ValueError(
            f"{ticker}: Negative volume found"
        )

    # High and low consistency
    if (
        (df["High"] < df["Low"]).any()
        or (
            df["High"]
            < df[["Open", "Close"]].max(axis=1)
        ).any()
        or (
            df["Low"]
            > df[["Open", "Close"]].min(axis=1)
        ).any()
    ):
        raise ValueError(
            f"{ticker}: Inconsistent high/low prices"
        )

    # Exclude weekend records
    weekend_rows = df["Date"].dt.day_of_week >= 5

    if weekend_rows.any():

        print(
            f"WARNING: {ticker}: "
            f"{weekend_rows.sum()} weekend records excluded"
        )

        df = df.loc[~weekend_rows].copy()

    if df.empty:
        raise ValueError(
            f"{ticker}: No valid records remain"
        )

    return df


# --------------------------------------------------
# GET OR CREATE DATA SOURCE
# --------------------------------------------------

def get_source_id(source_type):

    source_name = SOURCE_NAMES[source_type]

    with engine.begin() as connection:

        source_id = connection.execute(
            text("""
                SELECT source_id
                FROM data_sources
                WHERE source_name = :source_name
            """),
            {"source_name": source_name}
        ).scalar()

        if source_id is None:

            source_id = connection.execute(
                text("""
                    INSERT INTO data_sources (
                        source_name,
                        source_type
                    )
                    VALUES (
                        :source_name,
                        :source_type
                    )
                    RETURNING source_id
                """),
                {
                    "source_name": source_name,
                    "source_type": source_type
                }
            ).scalar_one()

    return source_id


# --------------------------------------------------
# IMPORT ONE STOCK FILE
# --------------------------------------------------

def import_stock_file(csv_file):

    ticker = csv_file.stem

    print(f"\nProcessing: {ticker}")

    df, source_type = load_csv(csv_file)

    df = validate_data(df, ticker)

    with engine.begin() as connection:

        instrument_id = connection.execute(
            text("""
                SELECT instrument_id
                FROM instruments
                WHERE ticker = :ticker
            """),
            {"ticker": ticker}
        ).scalar()

    if instrument_id is None:
        raise ValueError(
            f"{ticker}: Instrument not found in database"
        )

    source_id = get_source_id(source_type)

    records = []

    for _, row in df.iterrows():

        records.append({
            "instrument_id": instrument_id,
            "price_date": row["Date"].date(),
            "open_price": float(row["Open"]),
            "high_price": float(row["High"]),
            "low_price": float(row["Low"]),
            "close_price": float(row["Close"]),
            "adjusted_close": None,
            "volume": int(row["Volume"]),
            "source_id": source_id
        })

    with engine.begin() as connection:

        result = connection.execute(
            text("""
                INSERT INTO daily_prices (
                    instrument_id,
                    price_date,
                    open_price,
                    high_price,
                    low_price,
                    close_price,
                    adjusted_close,
                    volume,
                    source_id
                )
                VALUES (
                    :instrument_id,
                    :price_date,
                    :open_price,
                    :high_price,
                    :low_price,
                    :close_price,
                    :adjusted_close,
                    :volume,
                    :source_id
                )
                ON CONFLICT (instrument_id, price_date)
                DO NOTHING
            """),
            records
        )

        inserted_count = result.rowcount

    print(f"Valid CSV records: {len(records)}")
    print(f"New records inserted: {inserted_count}")


# --------------------------------------------------
# MAIN INGESTION PROCESS
# --------------------------------------------------

def main():

    print("\n==========================")
    print("FINVEST IQ PRICE INGESTION")
    print("==========================")

    if not PRICE_FOLDER.exists():
        print(f"Price folder not found: {PRICE_FOLDER}")
        return

    csv_files = sorted(PRICE_FOLDER.glob("*.csv"))

    if not csv_files:
        print("No CSV files found.")
        return

    successful_files = 0
    failed_files = 0

    for csv_file in csv_files:

        if csv_file.stat().st_size == 0:
            print(f"\nSkipping empty file: {csv_file.name}")
            continue

        try:
            import_stock_file(csv_file)
            successful_files += 1

        except Exception as error:
            print(
                f"ERROR processing {csv_file.name}: {error}"
            )
            failed_files += 1

    print("\n--------------------------")
    print("INGESTION SUMMARY")
    print("--------------------------")
    print(f"Successful files: {successful_files}")
    print(f"Failed files: {failed_files}")
    print("Ingestion process finished.")


if __name__ == "__main__":
    main()
