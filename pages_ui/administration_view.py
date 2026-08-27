import streamlit as st

from services.admin_service import (
    can_change_user_status,
    create_system_user,
    get_all_users,
    get_audit_logs,
    update_user_status,
)

from services.audit_service import (
    log_activity
)


def show_administration():
    """
    Administrator-only interface for
    user management and audit logs.
    """

    # -----------------------------------------
    # ACCESS CONTROL
    # -----------------------------------------

    if (
        st.session_state.get(
            "role"
        )
        != "Administrator"
    ):

        st.error(
            "Administrator access is required."
        )

        return

    st.title(
        "System Administration"
    )

    st.caption(
        "Manage system users and review "
        "application audit activity."
    )

    users_tab, logs_tab = st.tabs(
        [
            "Users",
            "Audit Logs"
        ]
    )

    # =========================================
    # USERS TAB
    # =========================================

    with users_tab:

        st.subheader(
            "User Management"
        )

        users_df = (
            get_all_users()
        )

        if not users_df.empty:

            col1, col2, col3 = (
                st.columns(3)
            )

            col1.metric(
                "Total Users",
                len(
                    users_df
                )
            )

            col2.metric(
                "Active Users",
                int(
                    users_df[
                        "status"
                    ]
                    .eq(
                        "Active"
                    )
                    .sum()
                )
            )

            col3.metric(
                "Inactive Users",
                int(
                    users_df[
                        "status"
                    ]
                    .eq(
                        "Inactive"
                    )
                    .sum()
                )
            )

            st.dataframe(
                users_df[
                    [
                        "user_id",
                        "full_name",
                        "email",
                        "role",
                        "status",
                        "created_at",
                    ]
                ].rename(
                    columns={
                        "user_id":
                            "User ID",

                        "full_name":
                            "Full Name",

                        "email":
                            "Email",

                        "role":
                            "Role",

                        "status":
                            "Status",

                        "created_at":
                            "Created",
                    }
                ),
                use_container_width=True,
                hide_index=True
            )

        st.divider()

        # -------------------------------------
        # CREATE USER
        # -------------------------------------

        st.subheader(
            "Create User"
        )

        with st.form(
            "create_user_form"
        ):

            full_name = (
                st.text_input(
                    "Full Name"
                )
            )

            email = (
                st.text_input(
                    "Email Address"
                )
            )

            password = (
                st.text_input(
                    "Temporary Password",
                    type="password"
                )
            )

            confirm_password = (
                st.text_input(
                    "Confirm Password",
                    type="password"
                )
            )

            role = (
                st.selectbox(
                    "Role",
                    [
                        "Analyst",
                        "Administrator"
                    ]
                )
            )

            create_button = (
                st.form_submit_button(
                    "Create User",
                    use_container_width=True
                )
            )

        if create_button:

            if (
                not full_name
                or not email
                or not password
            ):

                st.warning(
                    "Complete all required fields."
                )

            elif password != (
                confirm_password
            ):

                st.error(
                    "Passwords do not match."
                )

            elif len(
                password
            ) < 8:

                st.error(
                    "Password must contain "
                    "at least 8 characters."
                )

            else:

                result = (
                    create_system_user(
                        full_name=
                            full_name,

                        email=
                            email,

                        password=
                            password,

                        role_name=
                            role
                    )
                )

                if result[
                    "success"
                ]:

                    log_activity(
                        st.session_state[
                            "user_id"
                        ],
                        f"Created {role} account "
                        f"for {email.strip().lower()}."
                    )

                    st.success(
                        result[
                            "message"
                        ]
                    )

                    st.rerun()

                else:

                    st.error(
                        result[
                            "message"
                        ]
                    )

        st.divider()

        # -------------------------------------
        # CHANGE USER STATUS
        # -------------------------------------

        st.subheader(
            "Activate / Deactivate User"
        )

        users_df = (
            get_all_users()
        )

        if users_df.empty:

            st.info(
                "No users are available."
            )

        else:

            user_options = {
                (
                    f"{row['full_name']} "
                    f"({row['email']})"
                ):
                    row["user_id"]

                for _, row
                in users_df.iterrows()
            }

            selected_label = (
                st.selectbox(
                    "Select User",
                    list(
                        user_options.keys()
                    )
                )
            )

            selected_user_id = (
                user_options[
                    selected_label
                ]
            )

            selected_record = (
                users_df[
                    users_df[
                        "user_id"
                    ]
                    == selected_user_id
                ]
                .iloc[0]
            )

            current_status = (
                selected_record[
                    "status"
                ]
            )

            st.write(
                f"Current status: "
                f"**{current_status}**"
            )

            if current_status == (
                "Active"
            ):

                new_active_status = (
                    False
                )

                button_label = (
                    "Deactivate User"
                )

            else:

                new_active_status = (
                    True
                )

                button_label = (
                    "Activate User"
                )

            if st.button(
                button_label
            ):

                if not (
                    can_change_user_status(
                        selected_user_id,
                        st.session_state[
                            "user_id"
                        ]
                    )
                ):

                    st.error(
                        "You cannot deactivate "
                        "your own active session."
                    )

                else:

                    success = (
                        update_user_status(
                            selected_user_id,
                            new_active_status
                        )
                    )

                    if success:

                        action = (
                            "activated"
                            if new_active_status
                            else "deactivated"
                        )

                        log_activity(
                            st.session_state[
                                "user_id"
                            ],
                            f"{action.title()} user "
                            f"{selected_record['email']}."
                        )

                        st.success(
                            f"User {action} "
                            "successfully."
                        )

                        st.rerun()

    # =========================================
    # AUDIT LOGS TAB
    # =========================================

    with logs_tab:

        st.subheader(
            "Audit Logs"
        )

        logs_df = (
            get_audit_logs()
        )

        if logs_df.empty:

            st.info(
                "No audit records "
                "are available."
            )

            return

        log_col1, log_col2 = (
            st.columns(2)
        )

        with log_col1:

            user_filter = (
                st.selectbox(
                    "Filter by User",
                    [
                        "All Users"
                    ]
                    +
                    sorted(
                        logs_df[
                            "user"
                        ]
                        .dropna()
                        .unique()
                        .tolist()
                    )
                )
            )

        with log_col2:

            activity_filter = (
                st.text_input(
                    "Search Activity"
                )
            )

        filtered_logs = (
            logs_df.copy()
        )

        if user_filter != (
            "All Users"
        ):

            filtered_logs = (
                filtered_logs[
                    filtered_logs[
                        "user"
                    ]
                    == user_filter
                ]
            )

        if activity_filter.strip():

            filtered_logs = (
                filtered_logs[
                    filtered_logs[
                        "activity"
                    ]
                    .str.contains(
                        activity_filter.strip(),
                        case=False,
                        na=False
                    )
                ]
            )

        st.caption(
            f"Showing "
            f"{len(filtered_logs):,} "
            f"of {len(logs_df):,} "
            "audit records."
        )

        st.dataframe(
            filtered_logs[
                [
                    "log_id",
                    "user",
                    "email",
                    "activity",
                    "created_at",
                ]
            ].rename(
                columns={
                    "log_id":
                        "Log ID",

                    "user":
                        "User",

                    "email":
                        "Email",

                    "activity":
                        "Activity",

                    "created_at":
                        "Date/Time",
                }
            ),
            use_container_width=True,
            hide_index=True
        )