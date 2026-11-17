---
created: 2026-11-12T00:00:00Z
updated: 2026-11-17T16:18:17Z
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
| `SESSION_IDLE_MINUTES` | Fermeture de la session après ce temps sans activité | `15` |
| `MAX_FAILED_LOGINS` | Échecs de connexion consécutifs avant blocage du compte | `5` |
| `SESSION_COOKIE_SECURE` | Le cookie de session ne voyage qu'en HTTPS. **Ne jamais mettre `false` sur un serveur** : seuls les tests automatiques, en http, le font | `true` |

## Points d'entrée

| Route | Rôle |
|---|---|
| `GET /api/v1/health` | Répond `{"status": "ok", "database": "reachable" \| "unreachable"}` |
| `POST /api/v1/users` | Crée un compte (administrateur, ou coordonnateur sans le rôle administrateur) et envoie le lien |
| `GET /api/v1/users` | Liste les comptes (administrateur, coordonnateur) |
| `PUT /api/v1/users/{id}/roles` | Change les rôles (administrateur) |
| `POST /api/v1/users/{id}/deactivate`, `/reactivate` | Désactive ou réactive un compte (administrateur) |
| `POST /api/v1/password/setup` | Choisit son mot de passe avec le jeton du lien, sans connexion |
| `GET /api/v1/history/users/{id}` | L'historique d'un compte, dans l'ordre (administrateur, coordonnateur) |
| `POST /api/v1/auth/login` | Connexion par numéro de badge et mot de passe ; pose le cookie de session `cfdc_session` |
| `POST /api/v1/auth/logout` | Ferme la session et efface le cookie |
| `GET /api/v1/auth/me` | La personne connectée |
| `POST /api/v1/users/{id}/unblock` | Débloque un compte (administrateur) |

Sans cookie de session, les routes protégées répondent `401 Vous n'êtes pas connecté.` ; avec une session expirée ou fermée, `401 Votre session a expiré, reconnectez-vous.`
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
- `unblock-user --badge B07-42` débloque un compte bloqué après 5 échecs de connexion (en attendant l'écran de US-009).
- `create-user` accepte un ou plusieurs `--role` parmi `secretary`, `coordinator`, `service_head`, `trainer`, `it_admin`, `direction`.

**Sur le serveur de test**, le plan gratuit de Render n'a pas de terminal : lancez la commande **depuis votre poste**, avec l'adresse de la base Neon et les réglages Brevo, pour que l'email parte vraiment et que le lien mène au serveur de test :

```bash
DATABASE_URL='postgresql://…neon.tech/…' APP_BASE_URL=https://cfdc-frontend.onrender.com SMTP_HOST=smtp-relay.brevo.com SMTP_PORT=587 SMTP_STARTTLS=true SMTP_USERNAME='…' SMTP_PASSWORD='…' EMAIL_SENDER='CFDC <adresse vérifiée>' uv run python -m app.cli create-admin --badge A01-01 --first-name Jean --last-name Paul --email jean.paul@example.test
```

Le serveur de test ne reçoit **que des données fictives** ; utilisez des adresses email que vous lisez vous-même.

## Journal des modifications

Chaque création, modification et suppression d'une ligne s'inscrit dans la table `audit_log` (US-003), **dans la même transaction** : auteur, heure, fiche, action, valeurs avant et après.

- **Une nouvelle table doit choisir** : soit `__audit__ = AuditPolicy(...)` sur son modèle (`app/dal/dal_audit.py`), avec ses champs `secret` (jamais recopiés) et `personal` (masqués à la lecture) ; soit une ligne dans `EXEMPT_TABLES`, avec la raison. Sinon, `tests/unit/test_audit_coverage.py` échoue.
- **Toute écriture déclare son auteur** avec `acting_as(...)`, dans la BLL. Sans auteur, l'enregistrement est refusé (`MissingAuditActorError`).
- **Les modifications « en bloc »** (`update(...)`, `delete(...)` de SQLAlchemy) ne sont **pas** vues par le journal : modifiez les objets un par un.
- **La base refuse** de modifier, supprimer ou vider `audit_log`, même en SQL à la main (déclencheur PostgreSQL).

## Connexion

- Chaque tentative est notée dans `login_attempts` (numéro de badge saisi, compte, réussite, motif), **jamais avec le mot de passe**.
- Au **5e échec consécutif**, le compte est bloqué ; le journal l'inscrit avec l'auteur « Blocage automatique (5 échecs) ». Une connexion réussie ou un déblocage remettent le compte à zéro.
- Un numéro de badge inconnu et un mauvais mot de passe donnent le même message, « Numéro de badge ou mot de passe incorrect. », et le même temps de réponse. Un compte bloqué ou désactivé n'est signalé comme tel qu'à qui a donné le bon mot de passe.
- Les sessions (`auth_sessions`) ne gardent que l'empreinte du jeton ; désactiver ou bloquer un compte ferme ses sessions dans la même transaction.

## Droits : protéger une nouvelle route

Chaque route de l'API est **soit publique, soit protégée** (US-007) ; `tests/unit/test_route_permissions.py` échoue sinon.

- **Protégée** : l'acteur vient de `require_roles(...)`, qui refuse les autres rôles en `403 Votre rôle ne permet pas cette action.` avant tout traitement :
  ```python
  actor: EntActor = Depends(require_roles(Role.IT_ADMIN, Role.COORDINATOR))
  ```
  `require_roles(*ANY_ROLE)` : il suffit d'être connecté.
- **Publique**, exprès : `dependencies=[Depends(public_route)]` sur le décorateur, et la route ajoutée à `PUBLIC` dans le test.
- **Les règles plus fines** (le coordonnateur ne crée pas d'administrateur, le dernier administrateur est protégé) restent dans la BLL.
