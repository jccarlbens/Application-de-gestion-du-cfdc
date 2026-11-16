from app.core.exceptions import NotAuthenticatedError
from app.entities.ent_user import EntActor


def get_current_actor() -> EntActor:
    """L'utilisateur connecté. La connexion arrive en US-004 : d'ici là,
    personne n'est connecté, et chaque route protégée répond 401. Les tests
    remplacent cette dépendance pour simuler un utilisateur."""
    raise NotAuthenticatedError("Vous n'êtes pas connecté.")
