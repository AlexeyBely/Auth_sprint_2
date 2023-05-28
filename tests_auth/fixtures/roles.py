import pytest
from sqlalchemy.orm.exc import DetachedInstanceError, ObjectDeletedError

from ..settings import settings
from ..testdata.db_models import User, UserRole


@pytest.fixture(scope='function')
def get_user_role(sqlalchemy_session):
    """
    Creates and returns 'user' role.
    """
    role = UserRole(name='user')
    sqlalchemy_session.add(role)
    sqlalchemy_session.commit()

    yield role

    try:
        sqlalchemy_session.query(UserRole).filter(UserRole.id == role.id).delete()
        sqlalchemy_session.commit()
    except DetachedInstanceError:
        pass
    except ObjectDeletedError:
        pass


@pytest.fixture(scope='function')
def get_user_with_test_role(sqlalchemy_session, get_user_data):
    """
    Creates and returns user with 'user' role.
    """
    role = UserRole(name='test')
    sqlalchemy_session.add(role)

    user = User(**get_user_data)
    user.roles.append(role)
    sqlalchemy_session.add(user)
    sqlalchemy_session.commit()

    yield user, role


@pytest.fixture(scope='session')
def get_superuser_role(sqlalchemy_session):
    """
    Returns 'superuser' role.
    It is expected that 'superuser' role was created automatically when the application was first started.
    """
    superuser_role = sqlalchemy_session.query(UserRole).filter_by(name='superuser').first()
    yield superuser_role


@pytest.fixture(scope='function')
async def clear_test_data(sqlalchemy_session):
    """
    Clear user roles except 'superuser'.
    """
    yield

    try:
        sqlalchemy_session.query(User).filter(
            User.email != settings.auth_superuser_email).delete(synchronize_session='fetch')
        sqlalchemy_session.query(UserRole).filter(UserRole.name != 'superuser').delete(synchronize_session='fetch')
        sqlalchemy_session.commit()
    except DetachedInstanceError:
        pass
    except ObjectDeletedError:
        pass
