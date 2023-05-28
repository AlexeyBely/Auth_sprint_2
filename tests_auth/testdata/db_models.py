import uuid
from datetime import datetime

import bcrypt
from sqlalchemy import Column, DateTime, ForeignKey, String, Table
from sqlalchemy.dialects.postgresql import BYTEA, UUID
from sqlalchemy.orm import backref, declarative_base, relationship

Base = declarative_base()


users_user_roles = Table(
    'users_user_roles',
    Base.metadata,
    Column('user_id', UUID(as_uuid=True), ForeignKey('user.id', ondelete="CASCADE"), primary_key=True),
    Column('role_id', UUID(as_uuid=True), ForeignKey('user_role.id', ondelete="CASCADE"), primary_key=True)
)


class User(Base):
    __tablename__ = 'user'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    email = Column(String, unique=True, nullable=False)
    full_name = Column(String)
    password = Column(BYTEA, nullable=False)
    salt = Column(BYTEA, nullable=False)
    roles = relationship('UserRole', secondary=users_user_roles, lazy='subquery', backref=backref('users', lazy=True))
    history_logs = relationship('LoginHistory', backref='user')

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

    def __repr__(self):
        return f'<User: {self.email}>'


class UserRole(Base):
    __tablename__ = 'user_role'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    name = Column(String(64), unique=True, nullable=False)

    def __init__(self, name: str):
        self.name = name


class LoginHistory(Base):
    __tablename__ = 'login_history'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)
    date = Column(DateTime, nullable=False, default=datetime.utcnow)
    user_id = Column(UUID(as_uuid=True), ForeignKey('user.id', ondelete="CASCADE"))

    def __init__(self, user_id: str):
        self.user_id = user_id
