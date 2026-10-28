from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import field_validator


class Settings(BaseSettings):
    DATABASE_URL: str
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str
    REDIS_URL: str
    OTP_SECRET_KEY: str
    ENVIRONMENT: str = "development"
    ALLOW_ORIGINS: str = ""
    ALLOW_METHODS: str = ""

    @field_validator("ALLOW_METHODS")
    def parse_allow_methods(cls, v) -> list[str]:
        return v.split(",") if v else []

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
