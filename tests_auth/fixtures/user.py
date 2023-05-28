import pytest

from ..settings import settings
from ..testdata.db_models import User


@pytest.fixture(scope='session')
def get_user_data():
    """
    Data to create test user.
    """
    return {'email': 'test@ex.com', 'password': 'qwerty', 'full_name': 'User 1'}


@pytest.fixture(scope='function')
async def get_user(get_user_data, sqlalchemy_session):
    """
    Creates and returns user.
    """
    user = User(**get_user_data)
    sqlalchemy_session.add(user)
    sqlalchemy_session.commit()
    yield user

    sqlalchemy_session.delete(user)
    sqlalchemy_session.commit()


@pytest.fixture(scope='function')
async def get_user_access_token(make_request, get_user_data):
    """
    Returns test user access token.
    """
    login_response = await make_request('/auth/login/', method='POST',
                                        body={'email': get_user_data.get('email'),
                                              'password': get_user_data.get('password')})
    access_token = login_response.body.get('access_token')
    return access_token


@pytest.fixture(scope='session')
async def get_superuser(sqlalchemy_session):
    """
    Returns superuser.
    It is expected that superuser was created automatically when the application was first started.
    """
    superuser = sqlalchemy_session.query(User).filter_by(email=settings.auth_superuser_email).first()
    yield superuser


@pytest.fixture(scope='function')
async def get_superuser_access_token(make_request, get_superuser):
    """
    Returns superuser access token.
    """
    login_response = await make_request('/auth/login/', method='POST',
                                        body={'email': settings.auth_superuser_email,
                                              'password': settings.auth_superuser_password})
    access_token = login_response.body.get('access_token')
    return access_token
