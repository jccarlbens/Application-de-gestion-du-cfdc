from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # Pas de valeur par défaut : l'adresse contient le mot de passe de la base.
    # Une variable manquante fait échouer le démarrage, au lieu de tourner sur
    # une base inattendue (SOLUTION_DESIGN.md, ADR 2 : PostgreSQL seulement).
    database_url: str
    environment: str = "development"
    log_level: str = "INFO"


settings = Settings()
