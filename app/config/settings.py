from pydantic_settings import BaseSettings


class Settings(BaseSettings):
  DATABASE_URL: str
  ACCOUNT_SID: str
  AUTH_TOKEN: str
  SLACK_WEBHOOK_URL: str
  FROM_PHONE_NUMBER: str

  class Config:
    env_file = ".env"


settings = Settings()