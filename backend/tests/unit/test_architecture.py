"""Fait respecter le sens des couches par une machine, pas par la mémoire.

project-docs/_ARCHITECTURE_EXPLAINED.md, partie 1 § Application contrainte.
Une règle s'ajoute ici le jour où elle devient vraie du projet, pas avant.
"""

import ast
from pathlib import Path

import pytest

APP = Path(__file__).resolve().parents[2] / "app"

# Ce que chaque couche n'a pas le droit d'importer.
FORBIDDEN = {
    "entities": ("app.dal", "app.bll", "app.api", "sqlalchemy", "fastapi"),
    "dal": ("app.bll", "app.api", "fastapi"),
    "bll": ("app.api", "sqlalchemy", "fastapi"),
}

# Les modules de ces couches portent le préfixe de leur couche.
PREFIXES = {"entities": "ent_", "dal": "dal_", "bll": "bll_", "api/v1/dto": "dto_"}

# Fichiers d'infrastructure, sans préfixe par conception.
UNPREFIXED = {"__init__.py", "database.py"}


def _layer_of(path: Path) -> str | None:
    parts = path.relative_to(APP).parts
    return parts[0] if parts[0] in FORBIDDEN else None


def _imports_of(path: Path) -> list[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"))
    names: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            names.extend(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            names.append(node.module)
    return names


SOURCES = sorted(APP.rglob("*.py"))


def test_finds_the_sources_it_must_watch() -> None:
    assert any(_layer_of(p) for p in SOURCES)


@pytest.mark.parametrize("path", SOURCES, ids=lambda p: str(p.relative_to(APP)))
def test_imports_respect_layer_direction(path: Path) -> None:
    layer = _layer_of(path)
    if layer is None:
        return
    for name in _imports_of(path):
        for forbidden in FORBIDDEN[layer]:
            assert not (name == forbidden or name.startswith(forbidden + ".")), (
                f"{path.relative_to(APP)} ({layer}) importe {name}"
            )


@pytest.mark.parametrize("folder,prefix", PREFIXES.items())
def test_layer_modules_carry_their_prefix(folder: str, prefix: str) -> None:
    for path in (APP / folder).glob("*.py"):
        if path.name in UNPREFIXED:
            continue
        assert path.name.startswith(prefix), f"{path.relative_to(APP)} devrait commencer par {prefix}"
