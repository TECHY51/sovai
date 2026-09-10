from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List


class Settings(BaseSettings):
    SOVAI_ENV: str = "development"
    SOVAI_VERSION: str = "0.1.0"
    SOVAI_BACKEND_HOST: str = "127.0.0.1"
    SOVAI_BACKEND_PORT: int = 8000
    SOVAI_BACKEND_CORS_ORIGINS: List[str] = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
    ]

    SOVAI_INFERENCE_ENDPOINT: str = "http://localhost:11434"
    SOVAI_INFERENCE_TIMEOUT_SECONDS: int = 120

    SOVAI_MODEL_CODING: str = "qwen2.5-coder:3b"
    SOVAI_MODEL_REASONING: str = "qwen3:4b"
    SOVAI_MODEL_VISION: str = "gemma3:4b"

    SOVAI_SANDBOX_TIMEOUT_SECONDS: int = 15
    SOVAI_SANDBOX_MAX_MEMORY_MB: int = 512
    SOVAI_SANDBOX_ALLOW_NETWORK: bool = False

    SOVAI_DATA_DIR: str = "data"
    SOVAI_KNOWLEDGE_BASE_DIR: str = "knowledge_base"
    SOVAI_ARTIFACTS_DIR: str = "data/artifacts"
    SOVAI_AUDIT_LOG_DIR: str = "data/logs"

    SOVAI_STRICT_AIRGAP_MODE: bool = True
    SOVAI_AUDIT_LOGGING_ENABLED: bool = True

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )


settings = Settings()
