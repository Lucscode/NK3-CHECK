from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    PROJECT_NAME: str = "Inventário Corporativo TI"
    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str = "super_secreta_para_desenvolvimento_substituir_em_prod"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7 # 7 days
    
    POSTGRES_SERVER: str = "localhost"
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "postgres"
    POSTGRES_DB: str = "inventory_db"
    
    @property
    def DATABASE_URI(self) -> str:
        return "sqlite+aiosqlite:///./inventory.db"
    
    model_config = SettingsConfigDict(env_file=".env")

settings = Settings()
