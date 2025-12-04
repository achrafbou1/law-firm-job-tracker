from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    AIRTABLE_TOKEN: str
    APIFY_API_KEY: str
    LAW_FIRMS_TABLE_ID: str = "tbl9ckUPR5i3ubE7U"
    LAW_FIRM_DB_ID: str = "app5hiJRe4T8LcPie"

settings = Settings()
