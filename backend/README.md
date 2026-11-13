---
created: 2026-11-12T00:00:00Z
updated: 2026-11-13T18:16:17Z
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
| `APP_BASE_URL` | Adresse de l'interface ; les liens envoyés par email y mènent | `http://localhost:8080` |
| `SMTP_HOST`, `SMTP_PORT` | Serveur d'email | `localhost`, `1025` (Mailpit) |
| `SMTP_USERNAME`, `SMTP_PASSWORD` | Identifiants SMTP (vides pour Mailpit). **Secret** | vides |
| `SMTP_STARTTLS` | Chiffrer la connexion (`true` pour Brevo) | `false` |
| `EMAIL_SENDER` | Expéditeur des emails | `CFDC <no-reply@cfdc.local>` |
| `PASSWORD_LINK_HOURS` | Validité du lien pour choisir son mot de passe | `48` |

## Points d'entrée

| Route | Rôle |
|---|---|
| `GET /api/v1/health` | Répond `{"status": "ok", "database": "reachable" \| "unreachable"}` |
| `POST /api/v1/users` | Crée un compte (administrateur, ou coordonnateur sans le rôle administrateur) et envoie le lien |
| `GET /api/v1/users` | Liste les comptes (administrateur, coordonnateur) |
| `PUT /api/v1/users/{id}/roles` | Change les rôles (administrateur) |
| `POST /api/v1/users/{id}/deactivate`, `/reactivate` | Désactive ou réactive un compte (administrateur) |
| `POST /api/v1/password/setup` | Choisit son mot de passe avec le jeton du lien, sans connexion |

Tant que la connexion (US-004) n'existe pas, les routes de `/users` répondent `401 Vous n'êtes pas connecté.`
| `GET /docs` | Documentation interactive de l'API |

## Comptes : les commandes

Un compte se crée sans mot de passe ; la personne reçoit par email un lien, valable 48 heures, pour choisir le sien. En attendant l'écran des comptes (US-009), deux commandes créent les comptes :

```bash
uv run python -m app.cli create-admin --badge A01-01 --first-name Jean --last-name Paul --email jean.paul@example.test
```

```bash
uv run python -m app.cli create-user --badge B07-42 --first-name Marie --last-name Joseph --email marie@example.test --role secretary --role trainer
```

- `create-admin` crée le **premier** administrateur et refuse de servir une seconde fois.
- `create-user` accepte un ou plusieurs `--role` parmi `secretary`, `coordinator`, `service_head`, `trainer`, `it_admin`, `direction`.

**Sur le serveur de test**, le plan gratuit de Render n'a pas de terminal : lancez la commande **depuis votre poste**, avec l'adresse de la base Neon et les réglages Brevo, pour que l'email parte vraiment et que le lien mène au serveur de test :

```bash
DATABASE_URL='postgresql://…neon.tech/…' APP_BASE_URL=https://cfdc-frontend.onrender.com SMTP_HOST=smtp-relay.brevo.com SMTP_PORT=587 SMTP_STARTTLS=true SMTP_USERNAME='…' SMTP_PASSWORD='…' EMAIL_SENDER='CFDC <adresse vérifiée>' uv run python -m app.cli create-admin --badge A01-01 --first-name Jean --last-name Paul --email jean.paul@example.test
```

Le serveur de test ne reçoit **que des données fictives** ; utilisez des adresses email que vous lisez vous-même.
