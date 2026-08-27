from services.risk_labelling import (
    create_labelled_dataset
)


def inspect_distribution():

    df, _ = (
        create_labelled_dataset()
    )

    labelled = (
        df[
            df[
                "target_risk"
            ]
            .notna()
        ]
    )

    counts = (
        labelled[
            "target_risk"
        ]
        .value_counts()
    )

    percentages = (
        labelled[
            "target_risk"
        ]
        .value_counts(
            normalize=True
        )
        * 100
    )

    print(
        "\nRISK CLASS DISTRIBUTION"
    )

    print("=" * 60)

    for risk in [
        "Low",
        "Medium",
        "High"
    ]:

        print(
            f"{risk}: "
            f"{counts.get(risk, 0):,} "
            f"("
            f"{percentages.get(risk, 0):.2f}%"
            f")"
        )


if __name__ == "__main__":

    inspect_distribution()