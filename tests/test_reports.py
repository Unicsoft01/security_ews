from services.report_service import (
    build_latest_analysis,
    get_priority_risk_analysis,
    prepare_export_dataframe,
)


def test_report_analysis():

    summary, df = (
        build_latest_analysis()
    )

    assert (
        summary[
            "states_assessed"
        ]
        == 37
    )

    assert len(
        df
    ) == 37


def test_risk_total():

    summary, df = (
        build_latest_analysis()
    )

    total = (
        summary[
            "low_risk"
        ]
        +
        summary[
            "medium_risk"
        ]
        +
        summary[
            "high_risk"
        ]
    )

    assert total == 37


def test_export_structure():

    summary, df = (
        build_latest_analysis()
    )

    export_df = (
        prepare_export_dataframe(
            df
        )
    )

    required = {
        "State/FCT",
        "Assessment Week",
        "Forecast Week",
        "Predicted Risk",
        "Confidence (%)",
    }

    assert required.issubset(
        set(
            export_df.columns
        )
    )


def test_priority_only_medium_high():

    summary, df = (
        build_latest_analysis()
    )

    priority = (
        get_priority_risk_analysis(
            df
        )
    )

    if not priority.empty:

        assert set(
            priority[
                "risk_level"
            ]
        ).issubset(
            {
                "High",
                "Medium",
            }
        )