import os
from functools import lru_cache
from typing import  Optional

from pydantic_settings import BaseSettings, SettingsConfigDict

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))


class Settings(BaseSettings):
    mode: str = "development"
    
    anthropic_api_key: Optional[str] = None
    groq_api_key: Optional[str] = None
    openai_api_key: Optional[str] = None
   
    model_config = SettingsConfigDict(
        env_file="../.env",
        env_file_encoding="utf-8",
        env_nested_delimiter="__",
        arbitrary_types_allowed=True,
        extra="ignore",
    )


@lru_cache()
def get_settings():
    return Settings()
