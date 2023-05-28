import string
import random

from http import HTTPStatus
from requests import post, get
from urllib.parse import urlencode

import messages
from database.db import db
from database.db_models import User, LoginHistory, ResourceOauth, UserDeviceType
from storage_token import get_storage_tokens
from tokens import TokenType, generate_token
from settings import api_settings
from storage_token import StorageTokens, get_storage_tokens


class OauthLoginService:
    """
    Authorization through social networks.

    get_client_id - returns client_id and link to request authorization code
    resource_login - returns access_token and refresh_token by authorization code
    to add a new resource, describe map _url_request_map and _resource_login_map
    and specify the implementation method
    """
    def __init__(self, storage: StorageTokens, session):
        self.storage = storage
        self.session = session    

    def get_client_id(self, name_resource: str):
        """return client_id and url_request for resource."""
        client = self._get_client(name_resource)
        if not client:
            return {'error': messages.NOT_RESOURCE}, HTTPStatus.CONFLICT
        client_id, client_secret = client
        url_request = self._url_request_map(name_resource, client_id)
        return {'client_id': client_id, 'url_request': url_request}, HTTPStatus.OK

    def resource_login(self, name_resource: str, code:  str):
        client = self._get_client(name_resource)
        if not client:
            return {'error': messages.NOT_RESOURCE}, HTTPStatus.CONFLICT
        email_error, full_name_status = self._resource_login_map(name_resource, client, code)
        if full_name_status == HTTPStatus.BAD_REQUEST:
            return email_error, full_name_status
        tokens = self._login_from_oauth(email_error, full_name_status, name_resource)
        return tokens, HTTPStatus.OK    

    # client_id metods
    def _url_request_map(self, name_resource: str, client: tuple):
        """Select resource."""
        map_ = {
            'yandex': self._yandex_url_request_code,
            'vk': self._vk_url_request_code,
        }
        return map_[name_resource](client)

    def _yandex_url_request_code(self, client_id: str) -> str:
        url_request_code = '{0}authorize?response_type=code&client_id={1}'.format(
            api_settings.yandex_base_url,
            client_id,
        )
        return url_request_code

    def _vk_url_request_code(self, client_id: str) -> str:
        data = {
            'client_id': client_id,
            'redirect_uri': api_settings.redirect_uri_vk,
            'display': 'popup',
            'scope': 4194304,
            'response_type': 'code',
        }
        url_request_code = api_settings.vk_base_url + 'authorize?' + urlencode(data)
        return url_request_code

    # resource_login metods
    def _resource_login_map(self, name_resource: str, client: tuple, code: str):
        """Select resource."""
        map_ = {
            'yandex': self._yandex_login,
            'vk': self._vk_login,
        }
        return map_[name_resource](client, code)

    def _yandex_login(self, client: tuple, code: str):
        client_id, client_secret = client
        data = {
            'grant_type': 'authorization_code',
            'code': code,
            'client_id': client_id,
            'client_secret': client_secret
        }
        query = urlencode(data)
        try:
            response = post(api_settings.yandex_base_url + "token", query)
        except Exception as e:
            return e.messages, HTTPStatus.BAD_REQUEST
        if response.status_code != HTTPStatus.OK:
            return response.json(), HTTPStatus.BAD_REQUEST
        access_token_ya = response.json()['access_token']
        headers = {'Authorization': f'OAuth {access_token_ya}'}
        data = {
            'format': 'json',
        }
        query = urlencode(data)
        try:
            response = get("https://login.yandex.ru/info", query, headers=headers)    
        except Exception as e:
            return e.messages, HTTPStatus.BAD_REQUEST
        data = response.json()
        full_name = data['login']
        return f'{full_name}@yandex.ru', full_name

    def _vk_login(self, client: tuple, code: str):
        client_id, client_secret = client
        data = {
            'redirect_uri': api_settings.redirect_uri_vk,
            'code': code,
            'client_id': client_id,
            'client_secret': client_secret
        }
        query = urlencode(data)
        try:            
            response = post(api_settings.vk_base_url + "access_token", query)
        except Exception as e:
            return e.messages, HTTPStatus.BAD_REQUEST
        
        if response.status_code != HTTPStatus.OK:
            return response.json(), HTTPStatus.BAD_REQUEST
        data = response.json()
        email = data['email']
        return email, f'vk user {email}'

    def _get_random_password(self) -> str:
        password_length = 20
        allowed_chars = string.ascii_letters + string.digits + string.punctuation
        password = ''.join(random.choice(allowed_chars) for _ in range(password_length))
        return password

    def _login_from_oauth(self, email: str, full_name: str, name_resource: str):
        user = User.query.filter_by(email=email).first()
        if not user:
            data = {'email': email,
                    'full_name': full_name,
                    'password': self._get_random_password()}
            user = User(**data)
            self.session.add(user)
            self.session.commit()
        access_token = generate_token(user, TokenType.access_token)
        refresh_token = generate_token(user, TokenType.refresh_token)
        # add tokens to storage
        self.storage.save_access_refresh_tokens(user.id, access_token, refresh_token)
        # add history
        data = {'user_id': user.id,
                'user_agent': f'login via authorization OAuth2.0 resource {name_resource}',
                'user_device_type': str(UserDeviceType.OTHER),}
        log = LoginHistory(**data)
        db.session.add(log)
        db.session.commit()
        return {'access_token': access_token, 'refresh_token': refresh_token}

    def _get_client(self, name_resource: str) -> tuple | None:
        resource = ResourceOauth.query.filter_by(name_resource=name_resource).first()    
        if not resource:
            return None
        return resource.client_id, resource.client_secret


oauth_login_service = OauthLoginService(get_storage_tokens(),db.session)


def get_oauth_login_service() -> OauthLoginService:
    return oauth_login_service
