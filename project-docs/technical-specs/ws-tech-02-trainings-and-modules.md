---
created: 2026-11-20T00:00:00Z
updated: 2026-11-23T16:29:06Z
---

# WS-02 — Formations et modules : implémentation

**Répond à :** comment le catalogue, les modules et les documents sont-ils construits, et qu'est-ce qui ne doit pas être « corrigé » par erreur ?
**Construit par :** Epic 2 (US-010 à US-013).
**Comportement :** `functional-specs/ws-func-02-trainings-and-modules.md`. **Journal :** `ws-tech-05-traceability.md`.

## Données

| Table | Contenu | Journal |
|---|---|---|
| `domains` | `name` (unique) | journalisée, sujet `domains` |
| `subdomains` | `domain_id`, `name` (unique dans le domaine : `uq_subdomains_domain_id_name`) | journalisée, sujet `subdomains` |
| `trainings` | `title`, `title_key` (unique), `description`, `subdomain_id` | journalisée, sujet `trainings` |
| `modules` | `training_id`, `title`, `title_key` (unique dans la formation : `uq_modules_training_id_title_key`), `description`, `trainer_id` (nullable), `created_at` | journalisée **sous sa formation** |
| `course_documents` | `module_id`, `file_name`, `content_type`, `size_bytes`, `storage_name` (unique, aléatoire), `uploaded_by`, `uploaded_at`, `replaced_by_id` | journalisée **sous la formation de son module** |

**Migrations :**
- `b88262b5a722` : domaines, sous-domaines et formations, avec la liste de départ ;
- `b5248710ae06` : modules ;
- `f17fc41a3361` : documents.

- **`title_key`** est l'intitulé ou le titre nettoyé (espaces en double et en bord retirés), puis mis en minuscules par `casefold()` (`bll_training.title_key`). Les accents comptent. Pour les formations et les modules, **c'est la contrainte de la base qui garantit l'unicité**, et la DAL traduit son refus en message français (`_DUPLICATES`, `_commit`). Pour les domaines et les sous-domaines, la BLL vérifie aussi d'avance, sans tenir compte des majuscules.
- **La liste de départ** a des identifiants fixes (`0b1e0c3a-0000-4000-8000-0000000000NN`), les mêmes sur chaque base. Elle est insérée en SQL par la migration, donc **hors du journal**.
- **L'ordre des modules et des documents** suit `created_at` ou `uploaded_at`, remplis par **`clock_timestamp()`**. **Ne pas revenir à `now()`** : `now()` donne la même heure à tout ce qu'écrit une transaction, et l'ordre de deux lignes écrites ensemble dépendrait du hasard.

## Règles (BLL)

- **`bll_training.py` :**
  - **constantes :** `CATALOGUE_READERS` (tous sauf le formateur), `TRAINING_WRITERS` (secrétaire, coordonnateur, chef de service, administrateur) ;
  - **modifications :** toute modification d'une fiche enregistrée est réservée à l'administrateur ;
  - **désignation :** `assign_trainer` laisse désigner le formateur d'un module vide, et refuse de changer un formateur déjà désigné à quiconque n'est pas administrateur ;
  - **formateur :** `_check_trainer` exige un compte actif ayant le rôle formateur. `update_module` laisse l'administrateur **garder** un formateur devenu inactif ; seul un **nouveau** formateur est vérifié ;
  - **« Mes modules » :** `my_modules(actor)` lit l'identifiant **de la session**, jamais un identifiant envoyé par l'écran.
- **`bll_document.py` :**
  - **`check_file` :** taille (`DOCUMENT_MAX_BYTES`, 25 Mo), extension, puis contenu :
    - `%PDF` ;
    - ZIP contenant `word/` ou `ppt/` ;
    - en-tête OLE2 `D0CF11E0A1B11AE1` pour `.doc` et `.ppt`.

    Seul le dernier élément du nom est gardé (`PurePath(...).name`).
  - **`can_open` :** l'administrateur toujours ; sinon un document **en vigueur**, et le rôle formateur **et** `trainer_id == actor.user_id`.

## Stockage des fichiers

- **`FileStore`** (`dal_document.py`) range les fichiers dans `DOCUMENTS_DIR`, sous un nom aléatoire (`uuid4().hex`), jamais sous le nom de l'utilisateur.
  - Le fichier est écrit dans un temporaire (`.upload-…`), puis mis à sa place avec `os.replace`.
  - **`DalDocument.add`** range le fichier, puis enregistre la fiche. En cas d'échec, il **efface le fichier** : pas de fichier orphelin. Remplacer, c'est un `add(..., replaces=id)` qui marque l'ancien document dans la même transaction.
- **`DOCUMENTS_DIR`** vaut :
  - `/data/documents` (volume `documents`) dans Docker Compose et sur Render ;
  - `./documents` en local (ignoré par Git).
- **Sur Render** (plan gratuit), le dossier se vide à chaque redémarrage ; c'est accepté pour le serveur de test (affinage de l'Epic 2, Q8).
- **Nginx** (`frontend/nginx/default.conf.template`) a `client_max_body_size 26m` et une `error_page 413`, qui renvoie `{"detail": "Le fichier dépasse 25 Mo."}`. **Sans ce réglage, Nginx refuse tout envoi de plus de 1 Mo.**
- **`python-multipart`** est nécessaire à FastAPI pour recevoir un fichier.

## Routes (`/api/v1`)

| Route | Accès (route) | Règle fine (BLL) |
|---|---|---|
| `GET /domains` | tous sauf formateur | |
| `POST /domains`, `PUT /domains/{id}`, `POST /domains/{id}/subdomains`, `PUT /subdomains/{id}` | administrateur | noms uniques |
| `GET /trainings`, `GET /trainings/{id}` | tous sauf formateur | |
| `POST /trainings` | secrétaire, coordonnateur, chef de service, administrateur | |
| `PUT /trainings/{id}` | administrateur | |
| `GET /trainings/{id}/modules` | tous sauf formateur | |
| `POST /trainings/{id}/modules`, `POST /modules/{id}/trainer` | ceux qui enregistrent | changer un formateur désigné : administrateur |
| `PUT /modules/{id}` | administrateur | |
| `GET /trainers` | ceux qui enregistrent | formateurs actifs, nom et badge seulement |
| `GET /trainings/{id}/documents` | tous sauf formateur | versions remplacées : administrateur |
| `POST /modules/{id}/documents`, `POST /documents/{id}/replace`, `GET /documents` | administrateur | |
| `GET /documents/{id}/download` | formateur, administrateur | formateur actuel, version en vigueur |
| `GET /me/modules` | formateur | modules de la session |

Le téléchargement est un `FileResponse` sous le nom d'origine, encodé selon la RFC 5987 (`filename*=utf-8''…`).

## Historique

- **Toutes les fiches** sont servies par une seule route, `GET /history/{genre}/{id}`. Les genres sont `users`, `trainings`, `domains` et `subdomains`, et les lecteurs de chaque genre sont listés dans `bll_history._READERS`.
- **Le nom de l'auteur** (`actor_name`) est lu dans `users` par une jointure de `DalAudit.history`.
- **À l'écran :** les phrases sont écrites par `entities/history/lib/describeEntry.ts`. `names` (`pages/training/model/useHistoryNames.ts`) permet de nommer les formateurs et les modules.
  - **Limite connue :** la direction ne lit pas la liste des formateurs. Elle voit « Formateur désigné pour « … » » avec « Détails », sans le nom, quand ce formateur n'est plus sur aucun module.

## Frontend

- **Entités :**
  - `entities/training` : catalogue, modules, formateurs, « Mes modules », `TrainingFields` ;
  - `entities/document` : appels, `formatSize`, `downloadUrl` ;
  - `entities/history` : panneau commun ;
  - `entities/viewer` : `canSeeCatalogue`, `canRecordTraining`, `isTrainer`.
- **Pages :** `trainings`, `training-new`, `training` (avec `ModulesSection`, `ModuleDocuments`), `domains`, `documents`, `my-modules`.
- **`shared/api.apiPostForm`** envoie un fichier ; le navigateur fixe lui-même l'en-tête `Content-Type`.

## Tests

À la clôture : 357 au backend (unitaires, et intégration sur PostgreSQL et sur un vrai dossier) et 123 au frontend.
- `tests/unit/files.py` fabrique un petit fichier de chaque format.
- `tests/unit/test_route_permissions.py` vérifie les rôles exacts de chaque route **et échoue si une route attendue manque**.
