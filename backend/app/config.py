from dataclasses import dataclass
import os


@dataclass(frozen=True)
class Settings:
    app_env: str
    postgres_db: str
    postgres_user: str
    postgres_password: str
    postgres_host: str
    postgres_port: int

    @property
    def database_url(self) -> str:
        return os.getenv(
            "DATABASE_URL",
            (
                f"postgresql://{self.postgres_user}:{self.postgres_password}"
                f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
            ),
        )


def get_settings() -> Settings:
    return Settings(
        app_env=os.getenv("APP_ENV", "development"),
        postgres_db=os.getenv("POSTGRES_DB", "proyecto2_bd"),
        postgres_user=os.getenv("POSTGRES_USER", "proy2"),
        postgres_password=os.getenv("POSTGRES_PASSWORD", "secret"),
        postgres_host=os.getenv("POSTGRES_HOST", "localhost"),
        postgres_port=int(os.getenv("POSTGRES_PORT", "5432")),
    )

