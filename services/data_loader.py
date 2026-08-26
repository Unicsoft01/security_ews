from pathlib import Path

import pandas as pd

from config.settings import RAW_DATA_PATH


def load_raw_dataset():
    """
    Load the original ACLED Excel workbook.

    Returns
    -------
    pandas.DataFrame
        Raw ACLED dataset.
    """

    file_path = Path(RAW_DATA_PATH)

    if not file_path.exists():
        raise FileNotFoundError(
            f"ACLED dataset was not found at: {file_path}"
        )

    if file_path.suffix.lower() not in [".xlsx", ".xls", ".csv"]:
        raise ValueError(
            "Unsupported dataset format. "
            "Only Excel and CSV files are allowed."
        )

    if file_path.suffix.lower() == ".csv":
        df = pd.read_csv(file_path)
    else:
        df = pd.read_excel(
            file_path,
            engine="openpyxl"
        )

    return df


def filter_nigeria(df):
    """
    Filter the ACLED dataset to Nigeria only.
    """

    if "COUNTRY" not in df.columns:
        raise KeyError(
            "COUNTRY column is missing from the dataset."
        )

    nigeria_df = df[
        df["COUNTRY"]
        .astype(str)
        .str.strip()
        .str.casefold()
        .eq("nigeria")
    ].copy()

    return nigeria_df


if __name__ == "__main__":

    data = load_raw_dataset()

    print("\nACLED DATASET LOADED SUCCESSFULLY")
    print("-" * 50)

    print(f"Rows: {len(data):,}")
    print(f"Columns: {len(data.columns)}")

    print("\nCOLUMN NAMES")
    print("-" * 50)

    for column in data.columns:
        print(column)

    nigeria = filter_nigeria(data)

    print("\nNIGERIA FILTER")
    print("-" * 50)

    print(f"Nigeria records: {len(nigeria):,}")

    if "ADMIN1" in nigeria.columns:
        print(
            f"States/FCT: "
            f"{nigeria['ADMIN1'].nunique()}"
        )