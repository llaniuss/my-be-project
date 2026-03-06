from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # Pydantic сам найдет эти переменные в .env или в системе
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    DATABASE_URL: str

    # Указываем, откуда брать данные
    model_config = SettingsConfigDict(env_file=".env")

# Создаем экземпляр настроек