from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    APP_NAME: str = "Система учёта успеваемости"
    DATABASE_URL: str = "sqlite:///./student_performance.db"
    SECRET_KEY: str = "super-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 часа

    class Config:
        env_file = ".env"


settings = Settings()