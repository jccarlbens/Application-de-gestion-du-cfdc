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
