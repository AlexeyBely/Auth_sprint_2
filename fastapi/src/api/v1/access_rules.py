from fastapi import Depends

from api.v1.auth import TokenData, authenticate


MANAGEMENT_ROLES = ['superuser']
PRIVILEGE_USER_ROLES = MANAGEMENT_ROLES + ['gold_user', 'volunteer']
REGULAR_USER_ROLES = PRIVILEGE_USER_ROLES + ['user']


def is_management_user(token_data: TokenData = Depends(authenticate)) -> bool:
    if not any([r in MANAGEMENT_ROLES for r in token_data.roles]):
        return False
    return True


def is_privilege_user(token_data: TokenData = Depends(authenticate)) -> bool:
    if not any([r in PRIVILEGE_USER_ROLES for r in token_data.roles]):
        return False
    return True


def access_regular_users(token_data: TokenData = Depends(authenticate)) -> bool:
    if not any([r in REGULAR_USER_ROLES for r in token_data.roles]):
        return False
    return True
