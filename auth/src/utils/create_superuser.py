from sqlalchemy.exc import IntegrityError

from database.db import db
from database.db_models import User, UserRole


def create_superuser_role():
    """Creates the 'superuser' role if it does not exist."""
    try:
        superuser_role = UserRole.query.filter_by(name='superuser').first()
        if superuser_role:
            raise ValueError('The role "superuser" already exists!')
        role = UserRole('superuser')
        db.session.add(role)
        db.session.commit()
    except IntegrityError:
        pass


def create_superuser(email: str, password: str, fullname: str | None = None):
    if not email or not password:
        raise ValueError('No email address or password specified! Superuser was not created!')
    superuser_role = UserRole.query.filter_by(name='superuser').first()
    if not superuser_role:
        create_superuser_role()
    super_user = User.query.filter_by(email=email).first()
    if not super_user:
        try:
            superuser = User(email, password, fullname)
            superuser.roles.append(superuser_role)
            db.session.add(superuser)
            db.session.commit()
        except IntegrityError:
            raise ValueError('The user with provided email already exists! Superuser was not created!')
