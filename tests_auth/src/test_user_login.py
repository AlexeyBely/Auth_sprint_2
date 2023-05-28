from http import HTTPStatus
import uuid

import pytest
import json

from ..conftest import HTTPResponse
from ..testdata.db_models import User
from ..settings import settings


pytestmark = pytest.mark.asyncio


async def test_get_user_by_id(make_request: HTTPResponse, get_user: User):

    response = await make_request(f'/auth/users/{str(get_user.id)}/', method='GET')

    actual = response.status
    expected = HTTPStatus.OK
    assert actual == expected, f'Expected status {expected} but got {actual}'

    actual = response.body
    created_at = str(get_user.created_at).replace(' ', 'T')
    expected = {'id': str(get_user.id), 'email': get_user.email,
                'full_name': get_user.full_name, 'created_at': created_at}
    assert actual == expected, f'The list of user expected\nExpected: {expected}\nActual: {actual}'


async def test_create_and_delete_user(make_request):

    url = '/auth/signup/'
    body = {'email': 'myNewMail@mail.ru', 'password': 'My_New_password', 'full_name': 'New Name'}
    response = await make_request(url, method='POST', body=body)
    response_body = response.body
    user_id = response_body['id']

    assert response_body['email'] == 'myNewMail@mail.ru'
    assert response_body['full_name'] == 'New Name'

    url = '/auth/login/'
    body = {'email': 'myNewMail@mail.ru', 'password': 'My_New_password'}
    response = await make_request(url, method='POST', body=body)
    access_t = response.body['access_token']

    assert response.status == HTTPStatus.OK

    url = f'/auth/users/{user_id}/'
    header = {'Authorization': f'Bearer {access_t}'}
    response = await make_request(url, method='DELETE', headers=header)

    assert response.status == HTTPStatus.OK


async def test_get_users(make_request, get_user: User, get_user_access_token):

    url = '/auth/users/'
    header = {'Authorization': f'Bearer {get_user_access_token}'}
    response = await make_request(url, method='GET', headers=header)

    assert response.status == HTTPStatus.OK

    actual = len(response.body)
    assert actual > 0


async def test_refresh_token(make_request):

    url = '/auth/signup/'
    body = {'email': 'refresh@mail.ru', 'password': 'refresh_token', 'full_name': 'refresh_token'}
    response = await make_request(url, method='POST', body=body)

    url = '/auth/login/'
    body = {'email': 'refresh@mail.ru', 'password': 'refresh_token'}
    response = await make_request(url, method='POST', body=body)
    access_t = response.body['access_token']
    refresh_t = response.body['refresh_token']

    assert response.status == HTTPStatus.OK

    url = '/auth/refresh-token/'
    header = {'Authorization': f'Bearer {refresh_t}'}
    response = await make_request(url, method='POST', headers=header)

    assert response.status == HTTPStatus.OK

    access_new_t = response.body['access_token']
    assert access_new_t != access_t

    url = '/auth/users/'
    header = {'Authorization': f'Bearer {access_new_t}'}
    response = await make_request(url, method='GET', headers=header)
    assert response.status == HTTPStatus.OK


async def test_logout_user(make_request):

    url = '/auth/signup/'
    body = {'email': 'logout@mail.ru', 'password': 'logout', 'full_name': 'logout'}
    response = await make_request(url, method='POST', body=body)

    url = '/auth/login/'
    body = {'email': 'logout@mail.ru', 'password': 'logout'}
    response = await make_request(url, method='POST', body=body)
    access_t = response.body['access_token']
    refresh_t = response.body['refresh_token']
    assert response.status == HTTPStatus.OK

    url = '/auth/logout/'
    header = {'Authorization': f'Bearer {access_t}'}
    response = await make_request(url, method='POST', headers=header)
    assert response.status == HTTPStatus.OK

    url = '/auth/refresh-token/'
    header = {'Authorization': f'Bearer {refresh_t}'}
    response = await make_request(url, method='POST', headers=header)
    assert response.status == HTTPStatus.UNAUTHORIZED


async def test_history_logins(make_request, session):

    url = '/auth/signup/'
    body = {'email': 'history@mail.ru', 'password': 'history', 'full_name': 'history'}
    response = await make_request(url, method='POST', body=body)
    user_id = response.body['id']

    for i in range(11):
        url = '/auth/login/'
        body = {'email': 'history@mail.ru', 'password': 'history'}
        response = await make_request(url, method='POST', body=body)
        access_t = response.body['access_token']

    url = settings.service_url + '/auth/login-history/'
    request_id = str(uuid.uuid4())
    header = {'Authorization': f'Bearer {access_t}', 
              'X-Request-Id': request_id}
    params = {'page': '2', 'size': '5'}

    async with session.get(url, params=params, headers=header, json=body) as response:
        response_boby = await response.text()
        paginate = json.loads(response_boby)    

    assert response.status == HTTPStatus.OK

    expected = paginate['items']
    assert len(expected) == 5

    expected = paginate['next_num']
    assert expected == 3

    expected = paginate['prev_num']
    assert expected == 1

    expected = paginate['total']
    assert expected == 11

    url = f'/auth/users/{user_id}/'
    header = {'Authorization': f'Bearer {access_t}'}
    response = await make_request(url, method='DELETE', headers=header)


async def test_unauthorized_user(make_request):

    url = '/auth/refresh-token/'
    header = {'Authorization': 'Bearer 123456789'}
    response = await make_request(url, method='POST', headers=header)

    assert response.status == HTTPStatus.UNAUTHORIZED