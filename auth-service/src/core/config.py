from pydantic import Field, HttpUrl
from pydantic_settings import BaseSettings, SettingsConfigDict
from dotenv import load_dotenv
from enum import Enum

load_dotenv()


class Settings(BaseSettings):

    project_name: str = Field(..., validation_alias='PROJECT_NAME')
    pg_url: HttpUrl = Field(..., validation_alias='POSTGRES_URL')
    redis_url: HttpUrl = Field(..., validation_alias='REDIS_URL')
    pg_host: str = Field(..., validation_alias='POSTGRES_HOST')
    pg_port: int = Field(..., validation_alias='POSTGRES_PORT')
    redis_host: str = Field(..., validation_alias='REDIS_HOST')
    redis_port: int = Field(..., validation_alias='REDIS_PORT')
    pg_user: str = Field(..., validation_alias='POSTGRES_USER')
    pg_password: str = Field(..., validation_alias='POSTGRES_PASSWORD')
    pg_db: str = Field(..., validation_alias='POSTGRES_DB')
    authjwt_secret_key: str = Field(..., validation_alias='SECRET_KEY')
    authjwt_time_access: str = Field(..., validation_alias='TIME_LIFE_ACCESS')
    authjwt_time_refresh: str = Field(..., validation_alias='TIME_LIFE_REFRESH')
    authjwt_token_location: set = Field(default={"cookies"})
    authjwt_cookie_csrf_protect: bool = Field(default=False)
    authjwt_access_cookie_key: str = Field(default='access_token_cookie')
    authjwt_refresh_cookie_key: str = Field(default='refresh_token_cookie')

    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8')

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
