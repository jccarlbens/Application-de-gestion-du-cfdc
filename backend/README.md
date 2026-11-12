---
created: 2026-11-12T00:00:00Z
updated: 2026-11-12T15:46:47Z
---

# backend — API de l'application CFDC

API FastAPI en couches `entities / dal / bll / api` (`project-docs/_ARCHITECTURE_EXPLAINED.md`, partie 1), sur PostgreSQL. Le produit est décrit dans `project-docs/PRD.md`, l'architecture dans `project-docs/SOLUTION_DESIGN.md` ; les règles pour les agents sont dans le `CLAUDE.md` et l'`AGENTS.md` de la racine.

## Commandes

Depuis `backend/`, avec [uv](https://docs.astral.sh/uv/) :

| Pour… | Commande |
|---|---|
| Installer les dépendances | `uv sync` |
| Appliquer les migrations | `uv run alembic upgrade head` |
| Lancer l'API (port 8000) | `uv run uvicorn app.main:app --reload` |
| Lancer les tests | `uv run pytest` |
| Créer une migration | `uv run alembic revision --autogenerate -m "description"` |

Les tests marqués `integration` ont besoin d'une vraie base PostgreSQL (`DATABASE_URL`) ; sans elle, ils sont ignorés. La façon la plus simple d'avoir une base en local est `docker compose up db` depuis la racine du dépôt.

## Variables d'environnement

Copiez `.env.example` en `.env`.

| Variable | Rôle | Défaut |
|---|---|---|
| `DATABASE_URL` | Adresse PostgreSQL (`postgresql://…`). **Obligatoire** : sans elle, l'API refuse de démarrer | — |
| `ENVIRONMENT` | `development`, `test` ou `production` | `development` |
| `LOG_LEVEL` | Niveau de journalisation | `INFO` |
| `PORT` | Port d'écoute dans le conteneur (fourni par Render) | `8000` |

## Points d'entrée

| Route | Rôle |
|---|---|
| `GET /api/v1/health` | Répond `{"status": "ok", "database": "reachable" \| "unreachable"}` |
| `GET /docs` | Documentation interactive de l'API |
