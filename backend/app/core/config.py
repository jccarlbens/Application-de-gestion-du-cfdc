from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # Pas de valeur par défaut : l'adresse contient le mot de passe de la base.
    # Une variable manquante fait échouer le démarrage, au lieu de tourner sur
    # une base inattendue (SOLUTION_DESIGN.md, ADR 2 : PostgreSQL seulement).
    database_url: str
    environment: str = "development"
    log_level: str = "INFO"

    # Adresse publique de l'interface : les liens envoyés par email y mènent.
    app_base_url: str = "http://localhost:8080"

    # Envoi des emails (US-002). Par défaut : Mailpit, en local, sans
    # chiffrement ni mot de passe. Sur le serveur de test : Brevo, avec STARTTLS
    # (SOLUTION_DESIGN.md, ADR 4 : aucun fournisseur codé en dur).
    smtp_host: str = "localhost"
    smtp_port: int = 1025
    smtp_username: str = ""
    smtp_password: str = ""
    smtp_starttls: bool = False
    email_sender: str = "CFDC <no-reply@cfdc.local>"

    # Durée de validité du lien pour choisir son mot de passe (US-002, décision 11).
    password_link_hours: int = 48

    # Connexion (US-004). La session se ferme après 15 minutes sans activité
    # (PRD.md §9) ; le compte se bloque au 5e échec consécutif (NFR.md).
    session_idle_minutes: int = 15
    max_failed_logins: int = 5
    # Le cookie ne voyage qu'en HTTPS. Seuls les tests automatiques, en http,
    # le désactivent ; jamais un serveur.
    session_cookie_secure: bool = True

    # Documents de cours (US-012) : le dossier où ranger les fichiers (le
    # volume `documents` dans Docker Compose), et leur taille maximale.
    documents_dir: str = "/data/documents"
    document_max_bytes: int = 25 * 1024 * 1024


settings = Settings()
