import os
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    nvidia_api_key: str = ""
    model: str = "deepseek-ai/deepseek-v4-flash"
    base_url: str = "https://integrate.api.nvidia.com/v1"
    max_iterations: int = 10
    temperature: float = 0.1

    @property
    def api_key(self) -> str:
        return self.nvidia_api_key or os.getenv("NVIDIA_API_KEY", "")

    @classmethod
    def create(cls, **kwargs) -> "Settings":
        return cls(**kwargs)


settings = Settings()
