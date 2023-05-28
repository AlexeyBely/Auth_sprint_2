from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

from settings import api_settings as a_s


db_uri = (f'postgresql://{a_s.auth_postgres_user}:{a_s.auth_postgres_password}'
          f'@{a_s.auth_postgres_host}:{a_s.auth_postgres_port}/{a_s.auth_postgres_db}')
engine_psql = create_engine(db_uri)
session_psql = sessionmaker(autocommit=False, autoflush=False, bind=engine_psql)
