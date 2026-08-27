import pandas as pd


def get_feature_importance(
    pipeline
):

    preprocessor = (
        pipeline.named_steps[
            "preprocessor"
        ]
    )

    classifier = (
        pipeline.named_steps[
            "classifier"
        ]
    )

    feature_names = (
        preprocessor
        .get_feature_names_out()
    )

    importance = pd.DataFrame(
        {
            "feature":
                feature_names,

            "importance":
                classifier
                .feature_importances_,
        }
    )

    importance = (
        importance.sort_values(
            "importance",
            ascending=False
        )
        .reset_index(
            drop=True
        )
    )

    return importance




