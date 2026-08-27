import bcrypt


def hash_password(password):
    """
    Convert plain-text password into
    a secure bcrypt password hash.
    """

    password_bytes = (
        password.encode(
            "utf-8"
        )
    )

    hashed = bcrypt.hashpw(
        password_bytes,
        bcrypt.gensalt()
    )

    return hashed.decode(
        "utf-8"
    )


def verify_password(
    password,
    password_hash
):
    """
    Verify plain password against
    stored bcrypt hash.
    """

    return bcrypt.checkpw(
        password.encode(
            "utf-8"
        ),
        password_hash.encode(
            "utf-8"
        )
    )