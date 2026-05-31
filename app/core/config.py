from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import BaseModel
from pathlib import Path

BASE_DIR = Path(__file__).parents[2]

class DBConfig(BaseModel):
    url: str 
    echo: bool = False


class JWTConfig(BaseModel):
    algorithm: str 
    secret_key: str 
    expire_access_token_minutes: int
    expire_refresh_token_days: int 

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        case_sensitive=False,
        extra='ignore',
        env_nested_delimiter="__",
        env_file=BASE_DIR / ".env"
    )
    root_path: str = '/api/v1'
    app_name: str = "App"
    debug: bool = True
    db: DBConfig
    jwt: JWTConfig

settings = Settings()
