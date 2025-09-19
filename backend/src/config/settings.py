from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8', case_sensitive=False)

    app_name: str = Field(default="wall-graph", alias="APP_NAME")
    api_v1_prefix: str = Field(default="/api/v1", alias="API_V1_PREFIX")
    environment: str = Field(default="development", alias="ENVIRONMENT")
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")

    neo4j_uri: str = Field(default="bolt://localhost:7687", alias="NEO4J_URI")
    neo4j_adminuser: str = Field(default="neo4j", alias="NEO4J_ADMINUSER")
    neo4j_adminpassword: str = Field(default="pleasechangeme", alias="NEO4J_ADMINPASSWORD")
    neo4j_readonlyuser: str = Field(default="neo4j", alias="NEO4J_READONLYUSER")
    neo4j_readonlypassword: str = Field(default="pleasechangeme", alias="NEO4J_READONLYPASSWORD")
    google_api_key: str = Field(default="pleasechangeme", alias="GOOGLE_API_KEY")
    gcp_sa_key: str = Field(default="pleasechangeme", alias="GCP_SA_KEY")
    neo4j_database: str = Field(default="neo4j", alias="NEO4J_DATABASE")
    langfuse_secret_key: str = Field(default="pleasechangeme", alias="LANGFUSE_SECRET_KEY")
    langfuse_public_key: str = Field(default="pleasechangeme", alias="LANGFUSE_PUBLIC_KEY")
    lanfuse_host: str = Field(default="pleasechangeme", alias="LANGFUSE_HOST")


settings = Settings()  # type: ignore[misc] 