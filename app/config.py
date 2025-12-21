from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import BaseModel
from pathlib import Path

BASE_DIR = Path(__file__).parents[1] 

class DBConfig(BaseModel):
    db_url: str 
    echo: bool = False


class JWTConfig(BaseModel):
    algorithm: str 
    secret_key: str 
    expire_access_token_minutes: int
    expire_refresh_token_days: int 

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        case_sensitive=False,
        env_nested_delimiter="__",
        env_file=BASE_DIR / ".env"
    )
    db: DBConfig
    jwt: JWTConfig

settings = Settings()