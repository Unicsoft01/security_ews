import streamlit as st

from config.settings import (
    APP_NAME
)

from pages_ui.dashboard_view import (
    show_dashboard
)

from pages_ui.login_view import (
    show_login
)

from pages_ui.placeholder_view import (
    show_placeholder
)

from utils.session import (
    initialise_session,
    logout_session,
)

from services.audit_service import (
    log_activity
)

# Add a System Footer
from pages_ui.risk_assessment_view import (
    show_risk_assessment
)

from pages_ui.risk_map_view import (
    show_risk_map
)

from pages_ui.alerts_view import (
    show_alerts
)

from pages_ui.reports_view import (
    show_reports
)

from pages_ui.administration_view import (
    show_administration
)


# --------------------------------------------------
# STREAMLIT CONFIGURATION
# --------------------------------------------------

st.set_page_config(
    page_title=APP_NAME,
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)


# --------------------------------------------------
# SESSION INITIALISATION
# --------------------------------------------------

initialise_session()


# --------------------------------------------------
# LOGIN GATE
# --------------------------------------------------

if not st.session_state[
    "authenticated"
]:

    show_login()

    st.stop()


# --------------------------------------------------
# SIDEBAR USER INFORMATION
# --------------------------------------------------

st.sidebar.title(
    "AI Security EWS"
)

st.sidebar.success(
    f"Logged in as:\n\n"
    f"{st.session_state['full_name']}"
)

st.sidebar.caption(
    f"Role: "
    f"{st.session_state['role']}"
)


# --------------------------------------------------
# NAVIGATION OPTIONS
# --------------------------------------------------

navigation_options = [
    "Dashboard",
    "Dataset Management",
    "Data Processing",
    "Model Evaluation",
    "Risk Assessment",
    "Risk Map",
    "Alerts",
    "Reports",
]


if (
    st.session_state[
        "role"
    ]
    == "Administrator"
):

    navigation_options.append(
        "Administration"
    )


selected_page = (
    st.sidebar.radio(
        "Navigation",
        navigation_options
    )
)


# --------------------------------------------------
# LOGOUT
# --------------------------------------------------

st.sidebar.divider()

if st.sidebar.button(
    "Logout",
    use_container_width=True
):

    log_activity(
        st.session_state[
            "user_id"
        ],
        "User logged out of the system."
    )

    logout_session()

    st.rerun()


# --------------------------------------------------
# PAGE ROUTING
# --------------------------------------------------

if selected_page == (
    "Dashboard"
):

    show_dashboard()


elif selected_page == (
    "Dataset Management"
):

    show_placeholder(
        "Dataset Management",
        "Dataset management interface "
        "will be implemented in a "
        "subsequent phase."
    )


elif selected_page == (
    "Data Processing"
):

    show_placeholder(
        "Data Processing",
        "Data preprocessing and feature "
        "engineering interface."
    )


elif selected_page == (
    "Model Evaluation"
):

    show_placeholder(
        "Model Evaluation",
        "Decision Tree and Random Forest "
        "performance comparison."
    )


elif selected_page == (
    "Risk Assessment"
):

 show_risk_assessment()


elif selected_page == (
    "Risk Map"
):

    show_risk_map()


elif selected_page == (
    "Alerts"
):

    show_alerts()


elif selected_page == (
    "Reports"
):

    show_reports()


elif selected_page == (
    "Administration"
):

    show_administration()

# Add a System Footer
st.divider()

st.caption(
    "AI-Assisted Early Warning System "
    "for Security Threat Risk Assessment "
    "in Nigeria"
)