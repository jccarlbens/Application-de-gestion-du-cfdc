from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str = "sqlite:///./database/dev.db"
    environment: str = "development"
    log_level: str = "INFO"

    # Ajoutez ici les champs propres à ce service. Les secrets (clés de
    # signature JWT, clés d'API) n'ont AUCUNE valeur par défaut au niveau
    # Python — une variable d'environnement manquante doit faire échouer le
    # démarrage, et non tourner sans sécurité en silence. Consultez le
    # README.md de ce service pour savoir quelles variables il lui faut.


settings = Settings()
