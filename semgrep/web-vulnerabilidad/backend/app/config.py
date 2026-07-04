from functools import lru_cache
from pathlib import Path
from urllib.parse import quote_plus
import os

from dotenv import load_dotenv


BASE_DIR = Path(__file__).resolve().parents[1]
load_dotenv(BASE_DIR / ".env")


class Settings:
    db_host: str = os.getenv("DB_HOST", "localhost")
    db_port: int = int(os.getenv("DB_PORT", "3306"))
    db_user: str = os.getenv("DB_USER", "root")
    db_password: str = os.getenv("DB_PASSWORD", "")
    db_name: str = os.getenv("DB_NAME", "web_vulnerability_scanner")
    secret_key: str = os.getenv("SECRET_KEY", "change-me")
    algorithm: str = os.getenv("ALGORITHM", "HS256")
    access_token_expire_minutes: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "480"))
    frontend_origin: str = os.getenv("FRONTEND_ORIGIN", "http://localhost:3000")
    deepseek_api_key: str = os.getenv("DEEPSEEK_API_KEY", "")
    deepseek_api_url: str = os.getenv("DEEPSEEK_API_URL", "https://api.deepseek.com/chat/completions")
    deepseek_model: str = os.getenv("DEEPSEEK_MODEL", "deepseek-chat")

    @property
    def database_url(self) -> str:
        user = quote_plus(self.db_user)
        password = quote_plus(self.db_password)
        return (
            f"mysql+pymysql://{user}:{password}@{self.db_host}:{self.db_port}/"
            f"{self.db_name}?charset=utf8mb4"
        )

    @property
    def database_server_url(self) -> str:
        user = quote_plus(self.db_user)
        password = quote_plus(self.db_password)
        return f"mysql+pymysql://{user}:{password}@{self.db_host}:{self.db_port}/?charset=utf8mb4"


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()

