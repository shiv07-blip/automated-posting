from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    github_token: str | None = None
    telegram_token: str | None = None
    telegram_channel: str | None = None
    mastodon_instance: str | None = None
    mastodon_token: str | None = None


settings = Settings()
