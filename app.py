import streamlit as st
from config.settings import APP_NAME

st.set_page_config(
    page_title=APP_NAME,
    page_icon="🛡️",
    layout="wide"
)

st.title(APP_NAME)

st.subheader(
    "Security Threat Risk Assessment in Nigeria"
)

st.success(
    "Development environment successfully configured."
)

st.write(
    "ACLED Historical Security Incident Dataset"
)

st.info(
    "The system will use Decision Tree and "
    "Random Forest models to estimate weekly "
    "security risk levels."
)

# Testing database connection
import streamlit as st

from config.settings import APP_NAME
from database.connection import (
    check_database_connection
)


st.set_page_config(
    page_title=APP_NAME,
    page_icon="🛡️",
    layout="wide"
)


st.title(APP_NAME)

st.subheader(
    "Security Threat Risk Assessment "
    "in Nigeria"
)


db_status = (
    check_database_connection()
)


if db_status["connected"]:

    st.success(
        "Database connected successfully: "
        f"{db_status['database']}"
    )

else:

    st.error(
        "Database connection failed."
    )

    st.code(
        db_status["error"]
    )