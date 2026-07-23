from pydantic import BaseSettings, Field


class Settings(BaseSettings):
    cliniko_api_key: str = Field(..., env="CLINIKO_API_KEY")
    cliniko_base_url: str = Field("https://api.cliniko.com/v1", env="CLINIKO_BASE_URL")
    branch_location_map: dict[str, int] = Field(default_factory=dict, env="BRANCH_LOCATION_MAP")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
