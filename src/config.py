from pydantic_settings import BaseSettings

class Cfg(BaseSettings):
    svc_api_url: str


cfg = Cfg(_env_file=".env")  # type: ignore
__all__ = ["cfg"]
