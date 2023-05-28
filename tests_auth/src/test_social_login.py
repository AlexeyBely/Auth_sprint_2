from http import HTTPStatus
import uuid

import pytest

pytestmark = pytest.mark.asyncio


async def test_get_resources(make_request, get_superuser_access_token):

    url = '/auth/login_oauth/resources/'
    header = {'Authorization': f'Bearer {get_superuser_access_token}'}
    response = await make_request(url, method='GET', headers=header)

    assert response.status == HTTPStatus.OK

    actual = len(response.body)
    assert actual == 2


async def test_path_yandex_resource(make_request, get_superuser_access_token):

    url = '/auth/login_oauth/resources/'
    header = {'Authorization': f'Bearer {get_superuser_access_token}'}
    client_id = str(uuid.uuid1())
    body = {'name_resource': 'yandex', 'client_id': client_id, 'client_secret': 'client_secret'}
    response = await make_request(url, method='PATCH', headers=header, body=body)

    assert response.status == HTTPStatus.OK

    actual = response.body['name_resource']
    assert actual == 'yandex'

    actual = response.body['client_id']
    assert actual == client_id

    params = {'name_resource': 'yandex'}
    url = '/auth/login_oauth/client-id/'
    response = await make_request(url, method='GET', params=params)

    assert response.status == HTTPStatus.OK

    actual = response.body['client_id']
    assert actual == client_id


async def test_path_vk_resource(make_request, get_superuser_access_token):

    url = '/auth/login_oauth/resources/'
    header = {'Authorization': f'Bearer {get_superuser_access_token}'}
    client_id = str(uuid.uuid1())
    body = {'name_resource': 'vk', 'client_id': client_id, 'client_secret': 'client_secret'}
    response = await make_request(url, method='PATCH', headers=header, body=body)

    assert response.status == HTTPStatus.OK

    actual = response.body['name_resource']
    assert actual == 'vk'

    actual = response.body['client_id']
    assert actual == client_id

    params = {'name_resource': 'vk'}
    url = '/auth/login_oauth/client-id/'
    response = await make_request(url, method='GET', params=params)

    assert response.status == HTTPStatus.OK

    actual = response.body['client_id']
    assert actual == client_id


async def test_not_resource(make_request):
    params = {'name_resource': 'not_valid_resource'}
    url = '/auth/login_oauth/client-id/'
    response = await make_request(url, method='GET', params=params)

    assert response.status == HTTPStatus.UNPROCESSABLE_ENTITY