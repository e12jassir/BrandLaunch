import os
from dataclasses import dataclass

from dotenv import load_dotenv


DEFAULT_ENV_NAME = "development"
DEFAULT_SECRET_KEY = "dev-secret-key-change-me"
DEFAULT_DATABASE_PATH = "brandlaunch.sqlite"


@dataclass(frozen=True)
class Config:
    env_name: str = DEFAULT_ENV_NAME
    secret_key: str = DEFAULT_SECRET_KEY
    database_path: str = DEFAULT_DATABASE_PATH

    @classmethod
    def from_env(cls) -> "Config":
        load_dotenv()
        return cls(
            env_name=os.getenv("FLASK_ENV", DEFAULT_ENV_NAME),
            secret_key=os.getenv("SECRET_KEY", DEFAULT_SECRET_KEY),
            database_path=os.getenv("DATABASE_PATH", DEFAULT_DATABASE_PATH),
        )

    def to_flask_config(self) -> dict[str, str]:
        return {
            "ENV_NAME": self.env_name,
            "SECRET_KEY": self.secret_key,
            "DATABASE_PATH": self.database_path,
        }
