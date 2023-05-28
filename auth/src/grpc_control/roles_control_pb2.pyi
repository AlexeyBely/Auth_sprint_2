from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor

class NewRole(_message.Message):
    __slots__ = ["name"]
    NAME_FIELD_NUMBER: _ClassVar[int]
    name: str
    def __init__(self, name: _Optional[str] = ...) -> None: ...

class OperationResult(_message.Message):
    __slots__ = ["successful"]
    SUCCESSFUL_FIELD_NUMBER: _ClassVar[int]
    successful: bool
    def __init__(self, successful: bool = ...) -> None: ...

class ProvideRole(_message.Message):
    __slots__ = ["jti_to_compromised", "role_id", "user_id"]
    JTI_TO_COMPROMISED_FIELD_NUMBER: _ClassVar[int]
    ROLE_ID_FIELD_NUMBER: _ClassVar[int]
    USER_ID_FIELD_NUMBER: _ClassVar[int]
    jti_to_compromised: str
    role_id: str
    user_id: str
    def __init__(self, user_id: _Optional[str] = ..., role_id: _Optional[str] = ..., jti_to_compromised: _Optional[str] = ...) -> None: ...

class Role(_message.Message):
    __slots__ = ["name", "role_id"]
    NAME_FIELD_NUMBER: _ClassVar[int]
    ROLE_ID_FIELD_NUMBER: _ClassVar[int]
    name: str
    role_id: str
    def __init__(self, role_id: _Optional[str] = ..., name: _Optional[str] = ...) -> None: ...

class UserInfo(_message.Message):
    __slots__ = ["email"]
    EMAIL_FIELD_NUMBER: _ClassVar[int]
    email: str
    def __init__(self, email: _Optional[str] = ...) -> None: ...

class Uuid(_message.Message):
    __slots__ = ["id"]
    ID_FIELD_NUMBER: _ClassVar[int]
    id: str
    def __init__(self, id: _Optional[str] = ...) -> None: ...
