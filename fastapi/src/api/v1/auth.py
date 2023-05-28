import requests

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt

from core.config import api_settings
from models.auth import IsTokenCompromised, TokenData


oauth2_scheme = OAuth2PasswordBearer(tokenUrl='/auth/login/')
router = APIRouter()


def check_token_in_black_list(token: str) -> dict[str, bool]:
    url = api_settings.check_token_is_compromised_url
    try:
        response = requests.post(url, json={'access_token': token})
        return response.json()
    except Exception:
        return {'is_compromised': True}


async def authenticate(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, api_settings.access_token_secret_key, algorithms=[api_settings.token_algoritm])
        token_data = TokenData(**payload)
        is_compromised_data = check_token_in_black_list(token)
        check_compromised = IsTokenCompromised(**is_compromised_data)
        if check_compromised.is_compromised:
            raise JWTError('Token maybe compromised. Try login again and use new access token.')
    except JWTError as e:
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={'Authorization': 'Bearer'},
        )
        raise credentials_exception
    return token_data
