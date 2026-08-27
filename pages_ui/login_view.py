import streamlit as st

from services.auth_service import (
    authenticate_user
)

from utils.session import (
    login_session
)

from services.audit_service import (
    log_activity
)


def show_login():
    """
    Display system login interface.
    """

    st.markdown(
        """
        <div style="
            text-align:center;
            margin-top:40px;
        ">
            <h1>
                AI-Assisted Early Warning System
            </h1>

            <p>
                Security Threat Risk Assessment
                in Nigeria
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

    col1, col2, col3 = (
        st.columns(
            [
                1,
                1.4,
                1
            ]
        )
    )

    with col2:

        st.subheader(
            "System Login"
        )

        with st.form(
            "login_form"
        ):

            email = (
                st.text_input(
                    "Email Address"
                )
            )

            password = (
                st.text_input(
                    "Password",
                    type="password"
                )
            )

            submit = (
                st.form_submit_button(
                    "Login",
                    use_container_width=True
                )
            )

        if submit:

            if not email or not password:

                st.warning(
                    "Enter email and password."
                )

                return

            user = authenticate_user(
                email.strip(),
                password
            )

            if user is None:

                st.error(
                    "Invalid login details "
                    "or inactive account."
                )

                return

            login_session(
                user
            )

            log_activity(
                user[
                    "user_id"
                ],
                "User logged into the system."
            )

            st.success(
                "Login successful."
            )

            st.rerun()