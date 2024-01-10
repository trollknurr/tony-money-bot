import logging
from pathlib import Path

from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    BOT_TOKEN: SecretStr = Field(...)
    GROUP: int = Field(...)
    GOOGLE_SERVICE_ACCOUNT_FILE: Path = Field(default=Path("service_account.json"))

    GOOGLE_SHEET_URL: str = Field(...)


settings = Settings()

logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)

# set higher logging level for httpx to avoid all GET and POST requests being logged
logging.getLogger("httpx").setLevel(logging.WARNING)
