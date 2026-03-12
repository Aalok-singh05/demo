from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):

    GEMINI_API_KEY: str | None = None
    REPLICATE_API_TOKEN: str | None = None

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="allow"
    )


settings = Settings()