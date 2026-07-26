from pydantic import  Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    cliniko_api_key: str = Field(..., env="CLINIKO_API_KEY")
    cliniko_base_url: str = Field("https://api.cliniko.com/v1", env="CLINIKO_BASE_URL")
    bolna_api_key: str | None = Field(None, env="BOLNA_API_KEY")
    bolna_base_url: str = Field("https://api.bolna.ai", env="BOLNA_BASE_URL")
    bolna_agent_id: str | None = Field(None, env="BOLNA_AGENT_ID")
    bolna_from_phone_number: str | None = Field(None, env="BOLNA_FROM_PHONE_NUMBER")
    branch_location_map: dict[str, int] = Field(default_factory=dict, env="BRANCH_LOCATION_MAP")
    supabase_url :str = Field(None, env="SUPABASE_URL")
    supabase_key :str = Field(None,env="SUPABASE_KEY")
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
