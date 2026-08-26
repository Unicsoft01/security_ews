from pathlib import Path

from services.data_loader import (
    load_raw_dataset,
    filter_nigeria
)


OUTPUT_PATH = Path(
    "data/processed/"
    "acled_nigeria_raw.csv"
)


def export_nigeria_dataset():

    df = load_raw_dataset()

    nigeria = filter_nigeria(df)

    OUTPUT_PATH.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    nigeria.to_csv(
        OUTPUT_PATH,
        index=False
    )

    print(
        f"Nigeria dataset saved to: "
        f"{OUTPUT_PATH}"
    )

    print(
        f"Records saved: "
        f"{len(nigeria):,}"
    )


if __name__ == "__main__":
    export_nigeria_dataset()