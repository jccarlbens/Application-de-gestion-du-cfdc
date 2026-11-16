class AppError(Exception):
    """Base de chaque exception de domaine que ce service lève."""


# --- Niveau persistance : levées par la DAL, génériques pour toute entity ---


class NotFoundError(AppError):
    pass


class DuplicateKeyError(AppError):
    pass


# --- Niveau métier : levées par la BLL, spécifiques et porteuses de sens ---
#
# Ajoutez des exceptions ici à mesure que de vraies règles métier en ont
# besoin, par exemple `class DuplicateEmailError(AppError): pass`. Gardez des
# noms sémantiques et tournés vers le métier, jamais préfixés par une couche
# (PEP 8 : suffixe Error, pas de préfixe de couche) — voir
# project-docs/learnings/03-backend-layered-architecture-template.md pour
# savoir pourquoi.


class NotAuthenticatedError(AppError):
    """Aucun utilisateur connecté (la connexion arrive en US-004)."""


class ForbiddenError(AppError):
    """L'utilisateur est connecté, mais son rôle ne permet pas cette action."""


class InvalidInputError(AppError):
    """Une donnée saisie ne respecte pas une règle (badge, email, rôle…)."""


class DuplicateBadgeError(AppError):
    pass


class DuplicateEmailError(AppError):
    pass


class UserNotFoundError(AppError):
    pass


class LastAdminError(AppError):
    """Retirer le dernier administrateur actif laisserait l'application sans sentinelle."""


class AdminAlreadyExistsError(AppError):
    """`create-admin` ne sert qu'une fois : un administrateur existe déjà."""


class InvalidPasswordLinkError(AppError):
    """Le lien de mot de passe est inconnu, expiré ou déjà utilisé."""


class WeakPasswordError(AppError):
    pass


class EmailDeliveryError(AppError):
    """Le serveur d'email a refusé ou n'a pas répondu."""
