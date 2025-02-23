from pydantic import ConfigDict
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
  DATABASE_URL: str
  Account_SID: str
  Auth_Token: str
  
  class Config:
    env_file=".env"


settings = Settings()