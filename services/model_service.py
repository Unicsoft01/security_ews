from pathlib import Path

import joblib


# --------------------------------------------------
# SELECTED MODEL PATH
# --------------------------------------------------

SELECTED_MODEL_PATH = Path(
    "models/selected_model.pkl"
)


# --------------------------------------------------
# LOAD SELECTED MODEL
# --------------------------------------------------

def load_selected_model():
    """
    Load the final model selected during
    model evaluation.
    """

    if not SELECTED_MODEL_PATH.exists():

        raise FileNotFoundError(
            "Selected model was not found at: "
            f"{SELECTED_MODEL_PATH}"
        )

    model = joblib.load(
        SELECTED_MODEL_PATH
    )

    return model


# --------------------------------------------------
# VERIFY SELECTED MODEL
# --------------------------------------------------

def verify_selected_model():
    """
    Verify that the selected model can
    be successfully loaded.
    """

    model = (
        load_selected_model()
    )

    print(
        "\nSELECTED MODEL VERIFICATION"
    )

    print("=" * 60)

    print(
        "Model file:"
    )

    print(
        SELECTED_MODEL_PATH
    )

    print(
        "\nModel loaded successfully."
    )

    print(
        "\nPipeline type:"
    )

    print(
        type(model).__name__
    )

    # Inspect pipeline components
    if hasattr(
        model,
        "named_steps"
    ):

        print(
            "\nPipeline components:"
        )

        for name, component in (
            model.named_steps.items()
        ):

            print(
                f"- {name}: "
                f"{type(component).__name__}"
            )

    return model


# --------------------------------------------------
# RUN VERIFICATION
# --------------------------------------------------

if __name__ == "__main__":

    verify_selected_model()



import json


SELECTED_METADATA_PATH = Path(
    "models/selected_model_metadata.json"
)


def get_selected_model_info():

    if not SELECTED_METADATA_PATH.exists():

        raise FileNotFoundError(
            "Selected model metadata "
            "was not found."
        )

    with open(
        SELECTED_METADATA_PATH,
        "r",
        encoding="utf-8"
    ) as file:

        metadata = (
            json.load(file)
        )

    return metadata