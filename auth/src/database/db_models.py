import uuid
from datetime import datetime
from enum import Enum

import bcrypt
from sqlalchemy.dialects.postgresql import BYTEA, UUID
from sqlalchemy import UniqueConstraint

from database.db import db


users_user_roles = db.Table(
    'users_user_roles',
    db.Column('user_id', UUID(as_uuid=True), db.ForeignKey('user.id', ondelete="CASCADE"), primary_key=True),
    db.Column('role_id', UUID(as_uuid=True), db.ForeignKey('user_role.id', ondelete="CASCADE"), primary_key=True)
)


class User(db.Model):
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    email = db.Column(db.String, unique=True, nullable=False)
    full_name = db.Column(db.String)
    password = db.Column(BYTEA, nullable=False)
    salt = db.Column(BYTEA, nullable=False)
    roles = db.relationship('UserRole', secondary=users_user_roles, lazy='subquery',
                            backref=db.backref('users', lazy=True))
    history_logs = db.relationship('LoginHistory', backref='user')

    def __init__(self, email: str, password: str, full_name: str | None = None):
        self.email = email
        self.set_password(password)
        if full_name is not None:
            self.full_name = full_name

    @staticmethod
    def encrypt_password(password: str) -> tuple[bytes, bytes]:
        salt = bcrypt.gensalt()
        hashed_password = bcrypt.hashpw(password.encode('utf8'), salt)
        return hashed_password, salt

    def set_password(self, password: str):
        self.password, self.salt = self.encrypt_password(password)

    def check_password(self, password: str) -> bool:
        hashed_password = bcrypt.hashpw(password.encode('utf8'), self.salt)
        return hashed_password == self.password

    def __str__(self):
        return f'<User: {self.email}>'

    def __repr__(self):
        return f'<User: {self.email}>'


class UserRole(db.Model):
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    name = db.Column(db.String(64), unique=True, nullable=False)

    def update(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)

    def __init__(self, name: str):
        self.name = name

    def __str__(self):
        return f'<UserRole: {self.name}>'

    def __repr__(self):
        return f'<UserRole: {self.name}>'


class ResourceOauth(db.Model):
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)
    modifed_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    name_resource = db.Column(db.String, unique=True, nullable=False)
    client_id = db.Column(db.String, nullable=False)
    client_secret = db.Column(db.String, nullable=False)

    def __str__(self):
        return f'<Service: {self.name_service}>'

    def __repr__(self):
        return f'<Service: {self.name_service}>'


class UserDeviceType(Enum):
    PS = 'ps'
    MOBILE = 'mobile'
    OTHER = 'other'

    def __str__(self) -> str:
        return str(self.value)


def create_partition(target, connection, **kw) -> None:
    """ creating partition by login_history """
    connection.execute(
        """CREATE TABLE IF NOT EXISTS "login_history_ps" PARTITION OF "login_history" FOR VALUES IN ('ps')"""
    )
    connection.execute(
        """CREATE TABLE IF NOT EXISTS "login_history_mobile" PARTITION OF "login_history" FOR VALUES IN ('mobile')"""
    )
    connection.execute(
        """CREATE TABLE IF NOT EXISTS "login_history_other" PARTITION OF "login_history" FOR VALUES IN ('other')"""
    )


class LoginHistory(db.Model):
    __tablename__ = 'login_history' 
    __table_args__ = (
        UniqueConstraint('id', 'user_device_type'),
        {
            'postgresql_partition_by': 'LIST (user_device_type)',
            'listeners': [('after_create', create_partition)],
        }
    )
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False)
    date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    user_id = db.Column(UUID(as_uuid=True), db.ForeignKey('user.id', ondelete="CASCADE"))
    user_agent = db.Column(db.String)
    user_device_type = db.Column(db.String, primary_key=True)

    def __str__(self):
        return str(
                    {'date': str(self.date),
                     'device_type': self.user_device_type,
                     'user_agent': self.user_agent
                    }
                )

    def __repr__(self):
        return {'date': str(self.date),
                'device_type': self.user_device_type,
                'user_agent': self.user_agent
                }

