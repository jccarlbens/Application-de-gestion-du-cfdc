import re

from argon2 import PasswordHasher
from argon2.exceptions import VerificationError

from app.core.exceptions import WeakPasswordError

# Argon2id, l'algorithme que recommande l'OWASP (US-002, décision 7). Les
# paramètres par défaut de argon2-cffi suivent la RFC 9106.
_HASHER = PasswordHasher()

MIN_LENGTH = 8


def check_strength(password: str) -> None:
    """La règle de NFR.md § Sécurité : au moins 8 caractères, dont un chiffre."""
    if len(password) < MIN_LENGTH or not re.search(r"\d", password):
        raise WeakPasswordError("Le mot de passe doit faire au moins 8 caractères, dont au moins un chiffre.")


def hash_password(password: str) -> str:
    return _HASHER.hash(password)


def verify_password(password_hash: str, password: str) -> bool:
    try:
        return _HASHER.verify(password_hash, password)
    except VerificationError:
        return False
