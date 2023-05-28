from pydantic import BaseModel


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    user: str
    roles: list[str]
    lat: int
    exp: int
    jti: str


class IsTokenCompromised(BaseModel):
    is_compromised: bool