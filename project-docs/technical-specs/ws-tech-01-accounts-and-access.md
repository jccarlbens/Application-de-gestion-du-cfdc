---
created: 2026-11-17T00:00:00Z
updated: 2026-11-17T17:29:48Z
---

# WS-01 — Comptes et accès : implémentation

**Répond à :** comment les comptes, la connexion et les droits sont-ils construits, et qu'est-ce qui ne doit pas être « corrigé » par erreur ?
**Construit par :** Epic 1 (US-001 pour le socle, US-002, US-004, US-007, US-009). **Pas encore construit :** double authentification, mot de passe oublié (Epic 7).
**Comportement :** `functional-specs/ws-func-01-accounts-and-access.md`. **Journal :** `ws-tech-05-traceability.md`.

## Le socle (US-001)

- **Backend :** FastAPI en couches `entities / dal / bll / api`, en N-Layer : la BLL importe la DAL, sans interface intermédiaire (`_ARCHITECTURE_EXPLAINED.md` partie 2). Un test d'architecture vérifie le sens des imports.
  - SQLAlchemy 2, Alembic, PostgreSQL 16 avec le pilote `psycopg`, gestion par `uv`.
  - `DATABASE_URL` n'a **aucune valeur par défaut**, parce qu'elle contient le mot de passe. Les adresses `postgresql://` de Neon et de Render reçoivent le nom du pilote dans `app/dal/database.py`.
- **Frontend :** React 19, TypeScript, Vite, Tailwind 4 (jetons `brand-*` bleu et blanc dans `src/app/styles/index.css`), TanStack Query, React Router, en Feature-Sliced Design vérifié par Steiger ; tests Vitest.
- **Une seule adresse** pour l'interface et l'API : Vite relaie `/api` en développement, Nginx en conteneur (`frontend/nginx/default.conf.template`, variables `PORT` et `BACKEND_URL`). Le cookie `SameSite=Strict` en dépend (ADR 5).
- **Docker Compose** (`docker-compose.yml`) lance `db`, `backend`, `frontend` et `mailpit`, avec un volume `documents` prévu pour les documents de cours.
- **CI** (`.github/workflows/ci.yml`) : trois jobs, tous obligatoires pour fusionner sur `main`, avec une relecture approuvée.
  - `backend` : PostgreSQL 16 de service, migrations, tests ;
  - `frontend` : oxlint, Steiger, build, tests ;
  - `images` : construction des deux `Dockerfile`.
- **Serveur de test** (`render.yaml`) : deux services Docker gratuits sur Render, redéployés à chaque commit sur `main` ; la base est sur Neon. Données fictives seulement.

## Données

| Table | Contenu | Journal |
|---|---|---|
| `users` | `badge` (6 caractères, unique), `first_name`, `last_name`, `email` (unique), `phone`, canal de double authentification, `is_active`, `is_blocked`, `password_hash` (Argon2id, nul tant que non choisi), `failures_counted_since` | journalisée ; `password_hash` est **secret** |
| `user_roles` | une ligne par rôle (`user_id`, `role`), unique par compte | journalisée **sous le compte** |
| `password_tokens` | **empreinte SHA-256** du jeton de lien, expiration, date d'usage | exemptée |
| `login_attempts` | heure, badge saisi, compte s'il existe, réussite, motif ; **jamais le mot de passe** | exemptée |
| `auth_sessions` | **empreinte** du jeton du cookie, dernière activité, expiration, fermeture | exemptée |

- **Rôles :** les valeurs en base sont `secretary`, `coordinator`, `service_head`, `trainer`, `it_admin` et `direction` (`Role`, `app/entities/ent_user.py`).
- **Migrations :** `79d719cfde12` (comptes), `bb45920184ad` (journal), `8ec5285434bc` (connexion).

## Règles dans la BLL

- **`bll_user.py`** : les règles du badge (`[A-Z]\d{2}-\d{2}`, mis en majuscules), de l'email et des rôles, `_GRANTABLE_ROLES` (qui peut donner quel rôle), le dernier administrateur actif (`_refuse_if_last_admin`) et le déblocage.
- **Création atomique :** le compte, son lien et l'**envoi de l'email** se font dans une seule transaction. L'email part dans un rappel `before_commit` de la DAL ; s'il échoue, rien n'est enregistré et l'API répond `502`. **Ne pas sortir l'envoi de la transaction.**
- **Lien de mot de passe :** jeton `secrets.token_urlsafe(32)`, dont seule l'empreinte est stockée ; il est valable `PASSWORD_LINK_HOURS` (48 h).
  - `use_password_token` est une mise à jour ordinaire, avec un verrou de ligne (`FOR UPDATE`), pour que le journal la voie et que le lien ne serve pas deux fois.
  - Le lien n'est consommé qu'en cas de succès : réessayer après une erreur est sans risque.
- **`bll_auth.py` :** la connexion.
  - Le badge est mis en majuscules et chaque tentative est notée.
  - Un badge inconnu passe quand même par une vérification Argon2, pour garder **le même temps de réponse**.
  - Les échecs consécutifs se comptent dans `login_attempts`, **par numéro croissant (`id`) et non par heure**, puisque deux tentatives peuvent avoir la même heure ; on compte depuis la dernière réussite et depuis `failures_counted_since`, que pose un déblocage.
  - Au 5e échec (`MAX_FAILED_LOGINS`), le compte est bloqué avec pour auteur au journal « Blocage automatique (5 échecs) ».
  - Le compte n'est modifié, donc journalisé, **qu'au blocage** : un compteur dans `users` aurait écrit au journal à chaque mauvais mot de passe.
- **Fermeture des sessions :** `close_user_sessions` s'exécute dans la transaction qui désactive ou bloque le compte.
- **Mot de passe :** `bll_password.py` (`check_strength`, `hash_password` Argon2id).

## Session et cookie

- **Cookie `cfdc_session`** : `HttpOnly`, `Secure` (sauf `SESSION_COOKIE_SECURE=false` en local), `SameSite=Strict`. Il contient un jeton aléatoire ; la base n'en garde que l'empreinte.
- **Expiration :** `SESSION_IDLE_MINUTES` (15). Chaque requête authentifiée repousse `expires_at` (`DalAuth.use_session`).
- **`get_current_actor(request)`** (`app/api/v1/security.py`) lit le cookie et rend un `EntActor` (identifiant, rôles). Il répond `401` « Vous n'êtes pas connecté. » ou « Votre session a expiré, reconnectez-vous. », et l'interface distingue les deux.

## Droits : deux niveaux

1. **Sur la route :** chaque route déclare `Depends(public_route)` **ou** `Depends(require_roles(...))`. La garde porte un attribut `allowed_roles` et refuse en `403` avant tout traitement.
   - Les routes publiques sont `/health`, `/auth/login`, `/auth/logout` et `/password/setup`.
   - `tests/unit/test_route_permissions.py` échoue si une route n'est ni l'un ni l'autre. Il lit les routes effectives par `tests/unit/api_routes.py` (`effective_route_contexts()`), parce que depuis FastAPI 0.16x un routeur inclus apparaît dans `app.routes` comme **un seul objet**. Un test qui parcourt `app.routes` directement ne voit aucune route et **passe sans rien vérifier** : chaque test de routes vérifie d'abord qu'il en trouve.
2. **Dans la BLL :** les règles fines (le coordonnateur ne donne jamais le rôle d'administrateur, dernier administrateur…), avec l'acteur passé en paramètre.

| Route (`/api/v1`) | Accès |
|---|---|
| `GET /health` | publique |
| `POST /auth/login`, `POST /auth/logout` | publiques |
| `GET /auth/me` | tous les rôles (`ANY_ROLE`) |
| `POST /password/setup` | publique (le jeton fait foi) |
| `POST /users`, `GET /users`, `GET /users/by-badge/{badge}` | administrateur, coordonnateur |
| `PUT /users/{id}/roles`, `POST /users/{id}/deactivate`, `/reactivate`, `/unblock` | administrateur |
| `GET /history/users/{id}` | administrateur, coordonnateur |

**Codes d'erreur**, traduits en un seul endroit (`app/core/exception_handlers.py`) :

| Code | Cas |
|---|---|
| `401` | non connecté, session expirée |
| `403` | rôle insuffisant |
| `404` | compte inconnu |
| `409` | badge ou email pris, dernier administrateur, administrateur déjà créé |
| `410` | lien expiré ou utilisé |
| `422` | saisie invalide, mot de passe faible |
| `502` | email non parti |

## Emails

`app/dal/dal_email.py`, un client SMTP configuré par `SMTP_HOST`, `SMTP_PORT`, `SMTP_USERNAME`, `SMTP_PASSWORD`, `SMTP_STARTTLS` et `EMAIL_SENDER`.
- En local, les emails vont à Mailpit.
- Sur le serveur de test, ils partent par Brevo, avec les identifiants saisis dans Render, jamais dans le dépôt.
- Certains réseaux filtrent les ports SMTP (587, 2525) : une connexion qui s'ouvre puis ne répond plus vient du réseau, pas du code.

## Commandes

`app/cli.py` contient `create-admin`, `create-user` et `unblock-user --badge …`. Elles se lancent depuis le poste de l'administrateur, avec `DATABASE_URL` pointant sur Neon, puisque le plan gratuit de Render n'a pas de terminal. Au journal, leur auteur est « Ligne de commande (administrateur) ».

## Frontend

- **`entities/viewer`** : la personne connectée (`useViewer`, `logout`), les rôles et leurs libellés (`ROLE_LABELS`, `ALL_ROLES`), et les aides `canManageAccounts`, `isAdmin`, `grantableRoles`.
  - L'entité `account` l'importe par `entities/viewer/@x/account.ts`, l'entrée que Feature-Sliced Design prévoit entre deux entités ; Steiger refuse l'import direct.
- **`entities/account`** : appels à l'API des comptes, statut, tri, `StatusBadge`, et `describeEntry`, qui écrit une entrée du journal en phrase.
- **`widgets/app-shell`** : l'en-tête, le menu (`MENU`, `menuFor` : l'union des menus des rôles) et « Se déconnecter ». Sans session, il ramène à `/connexion`, avec `?expiree=1` si la session a expiré.
- **Pages :** `home`, `login`, `set-password`, `section` (« Bientôt disponible » ou accès refusé), `accounts`, `account-new`, `account`.
- **`shared/ui`** : `PageShell`, `ConfirmDialog` (fenêtre modale native, Échap annule) et `AccessDenied`.
- **`shared/api`** : `apiGet`, `apiPost`, `apiPostJson`, `apiPut` et `apiPostAction`. `genericMessage` traduit un `502`, `503` ou `504` venu du relais (« Le serveur est momentanément indisponible. Réessayez dans une minute. »), le temps que le backend gratuit de Render se réveille.

## Tests

À la clôture : 180 tests au backend (unitaires, et intégration sur un vrai PostgreSQL, annulés à la fin de chaque test) et 66 au frontend.
- **Les tests d'intégration ne supposent jamais une base vide :** ils ne regardent que ce qu'ils ont créé, puisque le journal ne se vide pas.
- Ils passent sur une base déjà remplie comme sur une base migrée de zéro (comme en CI).
