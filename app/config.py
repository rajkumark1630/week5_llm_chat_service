from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    openrouter_api_key: str
    api_key: str

    openrouter_model: str = "openai/gpt-4o-mini"
    max_input_tokens: int = 4000

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore"
    )


settings = Settings()