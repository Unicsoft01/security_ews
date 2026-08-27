import streamlit as st


def initialise_session():
    """
    Initialise required Streamlit session variables.
    """

    defaults = {
        "authenticated": False,
        "user_id": None,
        "full_name": None,
        "email": None,
        "role": None,
    }

    for key, value in (
        defaults.items()
    ):

        if key not in (
            st.session_state
        ):

            st.session_state[
                key
            ] = value


def login_session(user):
    """
    Store authenticated user in session.
    """

    st.session_state[
        "authenticated"
    ] = True

    st.session_state[
        "user_id"
    ] = user[
        "user_id"
    ]

    st.session_state[
        "full_name"
    ] = user[
        "full_name"
    ]

    st.session_state[
        "email"
    ] = user[
        "email"
    ]

    st.session_state[
        "role"
    ] = user[
        "role"
    ]


def logout_session():
    """
    Clear current authenticated session.
    """

    st.session_state[
        "authenticated"
    ] = False

    st.session_state[
        "user_id"
    ] = None

    st.session_state[
        "full_name"
    ] = None

    st.session_state[
        "email"
    ] = None

    st.session_state[
        "role"
    ] = None