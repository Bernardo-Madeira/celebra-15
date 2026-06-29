from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Configurações da aplicação, carregadas do .env."""

    database_url: str = "mysql+pymysql://celebra15:celebra15pass@localhost:3306/celebra15"

    secret_key: str = "troque-esta-chave-por-uma-string-aleatoria-segura"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60

    frontend_origin: str = "http://localhost:5173"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )


settings = Settings()
