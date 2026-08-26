from database.models import (
    Dataset,
    Location,
    Role,
    User
)


# ---------------------------------
# ROLE CRUD
# ---------------------------------

def get_role_by_name(
    db,
    role_name
):

    return (
        db.query(Role)
        .filter(
            Role.role_name == role_name
        )
        .first()
    )


# ---------------------------------
# USER CRUD
# ---------------------------------

def create_user(
    db,
    role_id,
    full_name,
    email,
    password_hash
):

    user = User(
        role_id=role_id,
        full_name=full_name,
        email=email,
        password_hash=password_hash
    )

    db.add(user)

    db.commit()

    db.refresh(user)

    return user


def get_user_by_id(
    db,
    user_id
):

    return (
        db.query(User)
        .filter(
            User.user_id == user_id
        )
        .first()
    )


def get_user_by_email(
    db,
    email
):

    return (
        db.query(User)
        .filter(
            User.email == email
        )
        .first()
    )


def update_user_status(
    db,
    user_id,
    status
):

    user = get_user_by_id(
        db,
        user_id
    )

    if not user:
        return None

    user.status = status

    db.commit()

    db.refresh(user)

    return user


def delete_user(
    db,
    user_id
):

    user = get_user_by_id(
        db,
        user_id
    )

    if not user:
        return False

    db.delete(user)

    db.commit()

    return True


# ---------------------------------
# DATASET CRUD
# ---------------------------------

def create_dataset_record(
    db,
    file_name,
    source,
    record_count,
    start_date,
    end_date,
    status="loaded"
):

    dataset = Dataset(
        file_name=file_name,
        source=source,
        record_count=record_count,
        start_date=start_date,
        end_date=end_date,
        status=status
    )

    db.add(dataset)

    db.commit()

    db.refresh(dataset)

    return dataset


def get_dataset_by_id(
    db,
    dataset_id
):

    return (
        db.query(Dataset)
        .filter(
            Dataset.dataset_id
            == dataset_id
        )
        .first()
    )


# ---------------------------------
# LOCATION CRUD
# ---------------------------------

def create_location(
    db,
    admin1,
    latitude=None,
    longitude=None
):

    location = Location(
        admin1=admin1,
        latitude=latitude,
        longitude=longitude
    )

    db.add(location)

    db.commit()

    db.refresh(location)

    return location


def get_location_by_admin1(
    db,
    admin1
):

    return (
        db.query(Location)
        .filter(
            Location.admin1 == admin1
        )
        .first()
    )