from services.risk_labelling import (
    create_labelled_dataset
)


def inspect_labels():

    df, thresholds = (
        create_labelled_dataset()
    )

    state = "Kaduna"

    columns = [
        "WEEK",
        "ADMIN1",
        "current_severity_score",
        "next_week_severity_score",
        "target_risk",
    ]

    state_df = (
        df[
            df["ADMIN1"]
            == state
        ][columns]
        .tail(20)
    )

    print(
        "\nRISK LABEL INSPECTION"
    )

    print("=" * 80)

    print(
        f"State: {state}"
    )

    print(
        f"Low threshold: "
        f"{thresholds['low_threshold']:.4f}"
    )

    print(
        f"High threshold: "
        f"{thresholds['high_threshold']:.4f}"
    )

    print("=" * 80)

    print(
        state_df.to_string(
            index=False
        )
    )


if __name__ == "__main__":

    inspect_labels()