from pydantic import Field
from pydantic_settings import BaseSettings
from dotenv import load_dotenv
from os import getenv
from enum import Enum

load_dotenv()


class Settings(BaseSettings):

    # С ЭТИМИ ЗНАЧЕНИЯМИ НЕ РАБОТАЕТ

    # redis_host: str = Field(..., env='REDIS_HOST')
    # redis_port: int = Field(..., env='REDIS_PORT')
    # pg_host: str = Field(..., env='POSTGRES_HOST')
    # pg_port: int = Field(..., env='POSTGRES_PORT')
    # pg_user: str = Field(..., env='POSTGRES_USER')
    # pg_db: str = Field(..., env='POSTGRES_DB')
    # pg_password: str = Field(..., env='POSTGRES_PASSWORD')
    # project_name: str = Field(..., env='PROJECT_NAME')
    # authjwt_secret_key: str = Field(..., env='SECRET_KEY')
    # authjwt_token_location: set = Field(default={"cookies"})
    # authjwt_cookie_csrf_protect: bool = False
    # authjwt_access_cookie_key: str = 'access_token_cookie'
    # authjwt_refresh_cookie_key: str = 'refresh_token_cookie'
    # authjwt_time_access: int = 100
    # authjwt_time_refresh: int = 180

    # С ЭТИМИ ЗНАЧЕНИЯМИ РАБОТАЕТ

    pg_user: str = getenv("POSTGRES_USER")
    pg_password: str = getenv("POSTGRES_PASSWORD")
    pg_host: str = getenv("POSTGRES_HOST")
    pg_port: int = getenv("POSTGRES_PORT")
    pg_db: str = getenv("POSTGRES_DB")
    redis_host: str = getenv("REDIS_HOST")
    redis_port: int = getenv("REDIS_PORT")
    project_name: str = getenv("PROJECT_NAME")
    authjwt_secret_key: str = getenv("SECRET_KEY")
    authjwt_time_access: str = getenv("TIME_LIFE_ACCESS")
    authjwt_time_refresh: str = getenv("TIME_LIFE_REFRESH")
    authjwt_token_location: set = {"cookies"}
    authjwt_cookie_csrf_protect: bool = False
    authjwt_access_cookie_key: str = 'access_token_cookie'
    authjwt_refresh_cookie_key: str = 'refresh_token_cookie'

    class Config:
        env_file = '.env'

    def database_dsn(self):
        return f"postgresql+asyncpg://{self.pg_user}:{self.pg_password}@{self.pg_host}:{self.pg_port}/{self.pg_db}"


class Token(Enum):
    ACCESS = 'access'
    REFRESH = 'refresh'
    BOTH = 'both'


class Name(Enum):
    USER = 'User'
    ROLE = 'Role'
    LOGIN = 'Login'
    EMAIL = 'Email'
    BOTH = 'user and role'


PAGE_SIZE = 10

app_settings = Settings()
