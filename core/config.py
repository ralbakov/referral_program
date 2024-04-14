import os
from pathlib import Path

from dotenv import load_dotenv
from pydantic import BaseModel
from pydantic_settings import BaseSettings

load_dotenv()

BASE_DIR = Path(__file__).cwd()


class DbSettings(BaseModel):
    POSTGRES_PASSWORD: str = os.environ['POSTGRES_PASSWORD']
    POSTGRES_USER: str = os.environ['POSTGRES_USER']
    POSTGRES_DB: str = os.environ['POSTGRES_DB']
    POSTGRES_HOST: str = os.environ['POSTGRES_HOST']
    url: str = f'postgresql+asyncpg://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:5432/{POSTGRES_DB}'
    create_db_url: str = f'postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:5432/{POSTGRES_DB}'


class AuthJWT(BaseModel):
    private_key_path: Path = BASE_DIR / 'certs' / 'jwt-private.key'
    public_key_path: Path = BASE_DIR / 'certs' / 'jwt-public.key'
    algorithm: str = 'RS256'
    access_token_expire_minutes: float = 30


class RedisSettings(BaseModel):
    host: str = os.environ['REDIS_HOST']
    port: int = int(os.environ['REDIS_PORT'])
    url: str = f'redis://{host}:{port}'
    exp_second_set: int = 600


class Email_SMTP_Server(BaseModel):
    smtp_host: str = 'smtp.gmail.com'
    smtp_port: int = 587
    email: str = os.environ['EMAIL_ADDRESS']
    password: str = os.environ['EMAIL_PASSWORD']


class Settings(BaseSettings):

    db: DbSettings = DbSettings()

    auth: AuthJWT = AuthJWT()

    cache: RedisSettings = RedisSettings()

    emailserver: Email_SMTP_Server = Email_SMTP_Server()


settings = Settings()
