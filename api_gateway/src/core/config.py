from pydantic import BaseModel, Field
from dotenv import load_dotenv

load_dotenv()


class Settings(BaseModel):
    project_name: str = Field(..., env='PROJECT_NAME')
    auth_port: str = Field(..., env='URL_PORT')
    auth_url: str = Field(..., env='URL_AUTH')

    def __init__(self, **data):
        super().__init__(**data)
        self.auth_url = f'http://{self.auth_url}:{self.auth_port}'

    class Config:
        env_file = '.env'


app_settings = Settings()
