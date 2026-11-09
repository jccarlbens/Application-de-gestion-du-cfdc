---
name: scaffold-backend-service
description: Générer la structure d'un nouveau service backend FastAPI + SQLAlchemy selon le motif d'architecture en couches de ce kit (Entities / DAL / BLL / DTO). À utiliser une fois que les PRD.md, CLAUDE.md et README.md d'un nouveau service existent déjà et qu'il est temps de poser sa véritable arborescence de dossiers. Scaffold a new FastAPI + SQLAlchemy backend service.
created: 2026-09-08T17:38:40Z
updated: 2026-11-09T17:14:13Z
---

# Compétence : générer la structure d'un service backend

## Pourquoi elle existe

Lisez d'abord `project-docs/_ARCHITECTURE_EXPLAINED.md` si le *pourquoi* d'une pièce quelconque ici n'est pas clair — la partie 1 explique les couches, la partie 5 la pile technique, et `project-docs/learnings/03-backend-layered-architecture-template.md` porte le raisonnement long. Cette compétence couvre le *comment*, pas le *pourquoi*. Elle existe pour que chaque service backend de ce projet démarre directement depuis la même structure établie, au lieu de la re-dériver (et de refaire les mêmes erreurs déjà corrigées) à chaque fois.

## Précondition dure — ne pas sauter

Selon le flux de travail « nouveau sous-projet » de ce kit (voir `CLAUDE.md` / `AGENTS.md` une fois écrits) : **aucun fichier source n'est créé avant que le périmètre ne soit convenu.** Avant d'exécuter cette compétence, `<service>/PRD.md`, `<service>/CLAUDE.md` et `<service>/README.md` doivent déjà exister. S'il en manque un, **arrêtez-vous et dites-le** — ne générez rien, et faites remarquer que le périmètre doit d'abord être convenu (remue-méninges → PRD → CLAUDE.md → README). Cette compétence ne s'exécute jamais qu'*après* ce point de passage, jamais à sa place.

## Ce que cette compétence ne fait *pas*

Elle ne construit que l'infrastructure — `core/`, `dal/database.py`, l'agrégateur de routeurs `api/v1/`, `main.py`, le câblage d'Alembic, `pyproject.toml`. Elle ne crée **aucun** fichier `entities/ent_*.py`, `dal/dal_*.py`, `bll/bll_*.py` ni `api/v1/dto/dto_*.py` — ceux-là sont du vrai travail fonctionnel, construit par user story via `user-story`, et non de la génération de structure. Un service fraîchement généré a un `api/v1/` vide (mais fonctionnel) avec rien de monté dedans.

## Procédure

```
Avancement de la génération :
- [ ] Étape 1 : confirmer la précondition (PRD / CLAUDE / README existent)
- [ ] Étape 2 : créer l'arborescence de dossiers
- [ ] Étape 3 : copier et adapter les fichiers gabarits
- [ ] Étape 4 : installer les dépendances
- [ ] Étape 5 : initialiser Alembic
- [ ] Étape 6 : vérifier que ça démarre réellement
- [ ] Étape 7 : rapporter
```

**Étape 1 — Confirmer la précondition.** Vérifiez que `<service>/PRD.md`, `<service>/CLAUDE.md` et `<service>/README.md` existent tous. Arrêtez-vous ici s'il en manque un (voir ci-dessus).

**Étape 2 — Créer l'arborescence de dossiers** à l'intérieur de `<service>/` :
```
app/{__init__.py, main.py}
app/core/__init__.py
app/entities/__init__.py
app/dal/__init__.py
app/bll/__init__.py
app/api/__init__.py
app/api/v1/__init__.py
app/api/v1/dto/__init__.py
database/.gitkeep
```

**Étape 3 — Copier et adapter les fichiers gabarits** depuis le dossier `templates/` de cette compétence (les chemins ci-dessous sont relatifs à ce dossier → relatifs à `<service>/`) :

| Gabarit | Destination | Adapter |
|---|---|---|
| `pyproject.toml` | `pyproject.toml` | Remplacez `{{SERVICE_NAME}}` par le nom du dossier du service. Ajoutez toute dépendance propre au service nommée dans son propre tableau de pile technique dans `CLAUDE.md`. |
| `core_config.py` | `app/core/config.py` | Ajoutez les champs `Settings` propres au service, selon le tableau des variables d'environnement de son `README.md` — les secrets n'ont pas de valeur par défaut (voir le commentaire déjà présent dans le gabarit). |
| `core_logging.py` | `app/core/logging.py` | Copier tel quel, aucun changement nécessaire. |
| `core_middleware.py` | `app/core/middleware.py` | Copier tel quel, aucun changement nécessaire. |
| `core_exceptions.py` | `app/core/exceptions.py` | Copier tel quel — commence avec seulement `AppError` / `NotFoundError` / `DuplicateKeyError` ; les exceptions métier s'ajoutent par user story. |
| `core_exception_handlers.py` | `app/core/exception_handlers.py` | Copier tel quel — commence vide ; les gestionnaires s'ajoutent par user story, à côté des exceptions métier ci-dessus. |
| `dal_database.py` | `app/dal/database.py` | Copier tel quel, aucun changement nécessaire. |
| `main.py` | `app/main.py` | Remplacez `{{SERVICE_TITLE}}` par le nom d'affichage du service. |
| `api_v1_init.py` | `app/api/v1/__init__.py` | Copier tel quel — les lignes d'inclusion de routeurs se décommentent ou s'ajoutent par user story. |
| `alembic_env.py` | *(utilisé à l'étape 5, pas copié directement pour l'instant)* | — |
| `env.example` | `.env.example` **et** `.env` | Ajoutez les variables propres au service, issues de son `README.md`. |
| `gitignore` | `.gitignore` | Copier tel quel, aucun changement nécessaire. |

**Étape 4 — Installer les dépendances.** Avec `uv` : `uv sync` depuis `<service>/` (crée `.venv`, installe les dépendances épinglées, installe le service lui-même en mode éditable, de sorte que `import app` fonctionne partout, y compris depuis Alembic, sans bidouille de `sys.path`). Avec `pip` simple : créez un `.venv`, puis `pip install -e .`.

**Étape 5 — Initialiser Alembic :**
1. `alembic init alembic` (via `uv run alembic init alembic` si vous utilisez `uv`).
2. Remplacez l'`alembic/env.py` généré par le `templates/alembic_env.py` de cette compétence (celui généré contient un squelette par défaut non câblé ; celui-ci est déjà correctement pointé vers `app.core.config.settings` et `app.dal.database.Base`).
3. Aucune migration à générer pour l'instant — il n'y a pas de modèle dans la DAL avant que la première user story n'en ajoute un.

**Étape 6 — Vérifier que ça démarre réellement.** Ne supposez pas que la structure générée est correcte — prouvez-le :
1. `uvicorn app.main:app --port 8000` en arrière-plan (ou sur le port de votre choix).
2. Vérifiez que la sortie du journal montre des lignes de démarrage propres au format structlog (`Started server process`, `Application startup complete`) sans aucune trace d'erreur.
3. `curl -s -o /dev/null -w "%{http_code}\n" http://127.0.0.1:8000/docs` → attendez `200`.
4. Arrêtez le serveur.

**Vérifiée de bout en bout dans un répertoire jetable le 2026-10-02**, avec `uv` 0.7.9 / Python 3.11 / FastAPI 0.142 / SQLAlchemy 2.1 / Alembic 1.20 / Pydantic 2.13 / uvicorn 0.54. Chaque étape s'est exécutée telle qu'écrite et **rien dans cette compétence n'a eu besoin d'être corrigé** : `uv sync` a installé le service en mode éditable, le remplacement de `alembic/env.py` a été prouvé par un `alembic current` qui a atteint le fichier SQLite à travers lui, et le serveur a démarré avec des lignes de démarrage au format structlog et un `/docs` → 200. Une surprise inoffensive qui vaut d'être connue : si un autre environnement virtuel est actif dans votre shell, `uv` affiche un avertissement `VIRTUAL_ENV does not match the project environment` et l'ignore, ce qui est le comportement correct et non un échec.

**Étape 7 — Rapporter.** Confirmez chaque fichier créé, que ça démarre proprement, et que l'étape suivante est la première vraie user story (via la création de `user-story`, ou l'affinage d'`epic` d'abord si le lot de user stories de ce service n'a pas encore été planifié) — c'est elle qui ajoutera les premiers fichiers `entities/`, `dal/`, `bll/` et `api/v1/dto/`.
