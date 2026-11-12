import os
from pathlib import Path

import pytest
from dotenv import load_dotenv

# Lit backend/.env s'il existe, sans écraser une variable déjà posée (dans
# GitHub Actions, DATABASE_URL vient du workflow).
load_dotenv(Path(__file__).resolve().parents[1] / ".env", override=False)

HAS_DATABASE = bool(os.environ.get("DATABASE_URL"))

# app.core.config exige DATABASE_URL dès l'import. Les tests unitaires n'ouvrent
# jamais de connexion : une adresse factice leur suffit.
os.environ.setdefault("DATABASE_URL", "postgresql://unused:unused@127.0.0.1:1/unused")


def pytest_collection_modifyitems(config, items):
    if HAS_DATABASE:
        return
    skip = pytest.mark.skip(reason="DATABASE_URL absent : test d'intégration ignoré")
    for item in items:
        if "integration" in item.keywords:
            item.add_marker(skip)
