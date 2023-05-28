from http import HTTPStatus

import pytest

pytestmark = pytest.mark.asyncio


# GET ROLE LIST

async def test_get_role_list(make_request, get_user_role, get_superuser_role, clear_test_data):
    """
    Test: /auth/roles/ endpoint returns the list of user roles.
    """
    response = await make_request('/auth/roles/', method='GET')

    actual = response.status
    expected = HTTPStatus.OK
    assert actual == expected, f'Expected status {expected} but got {actual}'

    actual = len(response.body)
    expected = 2
    assert actual == expected, f'Expected {expected} roles, but got {actual}'

    actual = response.body
    expected = [{'id': str(get_user_role.id), 'name': get_user_role.name},
                {'id': str(get_superuser_role.id), 'name': get_superuser_role.name}]
    assert all([a in expected for a in actual]), f'The list of user roles expected\nExpected: {expected}\nActual: {actual}'


# GET ROLE DETAIL

async def test_get_role_by_id(make_request, get_user_role, clear_test_data):
    """
    Test: /auth/roles/<id>/ endpoint returns the user role by ID.
    """
    response = await make_request(f'/auth/roles/{str(get_user_role.id)}/', method='GET')

    actual = response.status
    expected = HTTPStatus.OK
    assert actual == expected, f'Expected status {expected} but got {actual}'

    actual = response.body
    expected = {'id': str(get_user_role.id), 'name': get_user_role.name}
    assert actual == expected, f'The list of user roles expected\nExpected: {expected}\nActual: {actual}'


async def test_get_role_by_id_with_non_exist_id_returns_404(make_request, get_user_role, clear_test_data):
    """
    Test: /auth/roles/<id>/ endpoint returns the user role by ID.
    """
    response = await make_request('/auth/roles/00000000-0000-0000-0000-000000000000/', method='GET')

    actual = response.status
    expected = HTTPStatus.NOT_FOUND
    assert actual == expected, f'Expected status {expected} but got {actual}'


# CREATE ROLE

async def test_non_authorized_cannot_create_new_role(make_request, clear_test_data):
    """
    Test: /auth/roles/ endpoint - unauthorized can't create new role.
    """
    test_name = 'test role'
    response = await make_request('/auth/roles/', method='POST', body={'name': test_name})
    actual = response.status
    expected = HTTPStatus.UNAUTHORIZED
    assert actual == expected, f'Expected status {expected} but got {actual}'


async def test_superuser_can_create_new_role(make_request, get_superuser_access_token, clear_test_data):
    """
    Test: /auth/roles/ endpoint - superuser can create new role. Test unique role name.
    """
    test_name = 'test role'

    response = await make_request('/auth/roles/', method='POST', body={'name': test_name},
                                  headers={'Authorization': f'Bearer {get_superuser_access_token}'})
    actual = response.status
    expected = HTTPStatus.CREATED
    assert actual == expected, f'Expected status {expected} but got {actual}'

    # check if new role in role list
    response = await make_request('/auth/roles/')
    assert any([r.get('name') == test_name for r in response.body]), f'Expected that "{test_name}" role was created'

    # check if duplicated role name is not allowed
    response = await make_request('/auth/roles/', method='POST', body={'name': test_name},
                                  headers={'Authorization': f'Bearer {get_superuser_access_token}'})
    actual = response.status
    expected = HTTPStatus.CONFLICT
    assert actual == expected, f'The role name must be unique. Expected status {expected} but got {actual}'


async def test_not_superuser_cannot_create_role(make_request, get_user_access_token, clear_test_data):
    """
    Test: /auth/roles/ endpoint - user without 'superuser' role can't create new role.
    """
    response = await make_request('/auth/roles/', method='POST', body={'name': 'test role'},
                                  headers={'Authorization': f'Bearer {get_user_access_token}'})
    actual = response.status
    expected = HTTPStatus.UNAUTHORIZED
    assert actual == expected, f'Expected status {expected} but got {actual}'


# UPDATE ROLE

async def test_non_authorized_cannot_update_role(make_request, get_user_role, clear_test_data):
    """
    Test: PATCH /auth/roles/<id>/ - non-authorized user can't update role.
    """
    response = await make_request(f'/auth/roles/{str(get_user_role.id)}/', method='PATCH', body={'name': 'new role name'})

    actual = response.status
    expected = HTTPStatus.UNAUTHORIZED
    assert actual == expected, f'Expected status {expected} but got {actual}'

    response = await make_request(f'/auth/roles/{str(get_user_role.id)}/')
    actual = response.body.get('name')
    expected = get_user_role.name
    assert actual == expected, 'User role data should not be changed'


async def test_superuser_can_update_role(make_request, get_user_role, get_superuser_access_token, clear_test_data):
    """
    Test: PATCH /auth/roles/<id>/ - superuser can update role.
    """
    new_name = 'new role name'
    response = await make_request(f'/auth/roles/{str(get_user_role.id)}/', method='PATCH', body={'name': new_name},
                                  headers={'Authorization': f'Bearer {get_superuser_access_token}'})
    actual = response.status
    expected = HTTPStatus.OK
    assert actual == expected, f'Expected status {expected} but got {actual}'

    response = await make_request(f'/auth/roles/{str(get_user_role.id)}/')
    actual = response.body.get('name')
    expected = new_name
    assert actual == expected, f'User role data should be changed\nactual: {actual}\nexpected: {expected}'


async def test_not_superuser_cannot_update_role(make_request, get_user_role, get_user_access_token, clear_test_data):
    """
    Test: PATCH /auth/roles/<id>/ - user without 'superuser' role can't update role.
    """
    response = await make_request(f'/auth/roles/{str(get_user_role.id)}/', method='PATCH',
                                  body={'name': 'new role name'},
                                  headers={'Authorization': f'Bearer {get_user_access_token}'})
    actual = response.status
    expected = HTTPStatus.UNAUTHORIZED
    assert actual == expected, f'Expected status {expected} but got {actual}'

    response = await make_request(f'/auth/roles/{str(get_user_role.id)}/')
    actual = response.body.get('name')
    expected = get_user_role.name
    assert actual == expected, 'User role data should not be changed'


async def test_during_attempt_update_non_existed_role_the_correct_response(make_request, get_superuser_access_token,
                                                                           clear_test_data):
    """
    Test: PATCH /auth/roles/<id>/ endpoint - an attempt to delete non-existed user role.
    """
    response = await make_request('/auth/roles/00000000-0000-0000-0000-000000000000/', method='PATCH',
                                  body={'name': 'new role name'},
                                  headers={'Authorization': f'Bearer {get_superuser_access_token}'})
    actual = response.status
    expected = HTTPStatus.NOT_FOUND
    assert actual == expected, f'Expected status {expected} but got {actual}'


# DELETE ROLE

async def test_non_authorized_cannot_delete_role(make_request, get_user_role, clear_test_data):
    """
    Test: DELETE /auth/roles/<id>/ endpoint - non-authorized user can't delete role.
    """
    response = await make_request('/auth/roles/')
    roles_before_count = len(response.body)

    response = await make_request(f'/auth/roles/{get_user_role.id}/', method='DELETE')
    actual = response.status
    expected = HTTPStatus.UNAUTHORIZED
    assert actual == expected, f'Expected status {expected} but got {actual}'

    response = await make_request('/auth/roles/')
    roles_after_count = len(response.body)
    assert roles_before_count == roles_after_count, ('It is expected the number of roles is the same before and '
                                                     'afterto the DELETE request, but it did not happen. \n'
                                                     f'Roles before: {roles_before_count} '
                                                     f'Roles after: {roles_after_count}')


async def test_superuser_can_delete_role(make_request, get_superuser_access_token, get_user_role, clear_test_data):
    """
    Test: DELETE /auth/roles/<id>/ endpoint - superuser can delete role.
    """
    response = await make_request('/auth/roles/')
    roles_before_count = len(response.body)
    response = await make_request(f'/auth/roles/{get_user_role.id}/', method='DELETE',
                                  headers={'Authorization': f'Bearer {get_superuser_access_token}'})
    actual = response.status
    expected = HTTPStatus.NO_CONTENT
    assert actual == expected, f'Expected status {expected} but got {actual}'

    response = await make_request('/auth/roles/')
    roles_after_count = len(response.body)
    assert roles_before_count == roles_after_count + 1, ('It is expected the number of roles to decrease by 1 before '
                                                         'the DELETE request, but it did not happen. \n'
                                                         f'Roles before: {roles_before_count} '
                                                         f'Roles after: {roles_after_count}')


async def test_not_superuser_cannot_delete_role(make_request, get_user_access_token, get_user_role, clear_test_data):
    """
    Test: DELETE /auth/roles/<id>/ endpoint - user without 'superuser' role can delete role.
    """
    response = await make_request('/auth/roles/')
    roles_before_count = len(response.body)

    response = await make_request(f'/auth/roles/{get_user_role.id}/', method='DELETE',
                                  headers={'Authorization': f'Bearer {get_user_access_token}'})
    actual = response.status
    expected = HTTPStatus.UNAUTHORIZED
    assert actual == expected, f'Expected status {expected} but got {actual}'

    response = await make_request('/auth/roles/')
    roles_after_count = len(response.body)
    assert roles_before_count == roles_after_count, ('It is expected the number of roles is the same before and '
                                                     'afterto the DELETE request, but it did not happen. \n'
                                                     f'Roles before: {roles_before_count} '
                                                     f'Roles after: {roles_after_count}')


async def test_during_attempt_delete_non_existed_role_the_correct_response(make_request, get_superuser_access_token,
                                                                           clear_test_data):
    """
    Test: DELETE /auth/roles/<id>/ endpoint - an attempt to delete non-existed user role.
    """
    response = await make_request('/auth/roles/')
    roles_before_count = len(response.body)
    response = await make_request('/auth/roles/00000000-0000-0000-0000-000000000000/', method='DELETE',
                                  headers={'Authorization': f'Bearer {get_superuser_access_token}'})
    actual = response.status
    expected = HTTPStatus.NOT_FOUND
    assert actual == expected, f'Expected status {expected} but got {actual}'

    response = await make_request('/auth/roles/')
    roles_after_count = len(response.body)
    assert roles_before_count == roles_after_count, ('It is expected the number of roles is the same before and '
                                                     'afterto the DELETE request, but it did not happen. \n'
                                                     f'Roles before: {roles_before_count} '
                                                     f'Roles after: {roles_after_count}')


# PROVIDE ROLE

async def test_unauthorized_cannot_provide_role(make_request, get_user, get_superuser_access_token, get_user_role,
                                                clear_test_data):
    """
    Test: POST /auth/roles/provide/ endpoint - unauthorized user can't provide role to user.
    """
    response = await make_request('/auth/roles/provide/', method='POST',
                                  body={'user_id': str(get_user.id), 'role_id': str(get_user_role.id)})
    actual = response.status
    expected = HTTPStatus.UNAUTHORIZED
    assert actual == expected, f'Expected status {expected} but got {actual}'


async def test_superuser_can_provide_role(make_request, get_user, get_superuser_access_token, get_user_role,
                                          clear_test_data):
    """
    Test: POST /auth/roles/provide/ endpoint - superuser can provide role to user.
    """
    response = await make_request('/auth/roles/provide/', method='POST',
                                  body={'user_id': str(get_user.id), 'role_id': str(get_user_role.id)},
                                  headers={'Authorization': f'Bearer {get_superuser_access_token}'})
    actual = response.status
    expected = HTTPStatus.OK
    assert actual == expected, f'Expected status {expected} but got {actual}'


async def test_not_superuser_cannot_provide_role(make_request, get_user_access_token, get_user_with_test_role,
                                                 get_user_role, clear_test_data):
    """
    Test: POST /auth/roles/provide/ endpoint - superuser can't provide role to user.
    """
    user, role = get_user_with_test_role
    response = await make_request('/auth/roles/provide/', method='POST',
                                  body={'user_id': str(user.id), 'role_id': str(get_user_role.id)},
                                  headers={'Authorization': f'Bearer {get_user_access_token}'})
    actual = response.status
    expected = HTTPStatus.UNAUTHORIZED
    assert actual == expected, f'Expected status {expected} but got {actual}'


# # REVOKE ROLE

async def test_unauthorized_cannot_revoke_role(make_request, get_superuser_access_token, get_user_with_test_role,
                                               clear_test_data):
    """
    Test: POST /auth/roles/revoke/ endpoint - unauthorized user can't revoke user role.
    """
    user, role = get_user_with_test_role
    response = await make_request('/auth/roles/revoke/', method='POST',
                                  body={'user_id': str(user.id), 'role_id': str(role.id)})
    actual = response.status
    expected = HTTPStatus.UNAUTHORIZED
    assert actual == expected, f'Expected status {expected} but got {actual}'


async def test_superuser_can_revoke_role(make_request, get_superuser_access_token, get_user_with_test_role,
                                         clear_test_data):
    """
    Test: POST /auth/roles/revoke/ endpoint - superuser can revoke user role.
    """
    user, role = get_user_with_test_role
    response = await make_request('/auth/roles/revoke/', method='POST',
                                  body={'user_id': str(user.id), 'role_id': str(role.id)},
                                  headers={'Authorization': f'Bearer {get_superuser_access_token}'})
    actual = response.status
    expected = HTTPStatus.OK
    assert actual == expected, f'Expected status {expected} but got {actual}'


async def test_not_superuser_cannot_revoke_role(make_request, get_user_with_test_role, get_user_access_token,
                                                clear_test_data):
    """
    Test: POST /auth/roles/revoke/ endpoint - user without 'superuser' role can't revoke user role.
    """
    user, role = get_user_with_test_role
    response = await make_request('/auth/roles/revoke/', method='POST',
                                  body={'user_id': str(user.id), 'role_id': str(role.id)},
                                  headers={'Authorization': f'Bearer {get_user_access_token}'})
    actual = response.status
    expected = HTTPStatus.FORBIDDEN
    assert actual == expected, f'Expected status {expected} but got {actual}'
