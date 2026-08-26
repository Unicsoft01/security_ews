import pandas as pd
from config.settings import RAW_DATA_PATH


def load_raw_dataset():
    df = pd.read_excel(
        RAW_DATA_PATH,
        engine="openpyxl"
    )

    return df


if __name__ == "__main__":
    data = load_raw_dataset()

    print("Dataset loaded successfully.")
    print(f"Rows: {len(data):,}")
    print(f"Columns: {len(data.columns)}")
    print("\nColumns:")
    print(data.columns.tolist())

# Temporary code to filter Nigeria records and print the number of records and unique states/FCT
    nigeria = data[
    data["COUNTRY"].str.strip().str.lower()
    == "nigeria"
].copy()

print(
    f"Nigeria records: {len(nigeria):,}"
)

print(
    f"States/FCT: {nigeria['ADMIN1'].nunique()}"
)