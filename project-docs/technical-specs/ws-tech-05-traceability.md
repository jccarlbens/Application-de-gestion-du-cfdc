---
created: 2026-11-17T00:00:00Z
updated: 2026-11-23T16:29:06Z
---

# WS-05 — Corrections et traçabilité : implémentation

**Répond à :** comment le journal est-il construit, et comment une nouvelle table s'y branche-t-elle ?

> **Où commence cette spécification.** Elle ne couvre que **le journal**, construit par l'Epic 1 (US-003) et étendu par l'Epic 2 (US-010, US-012) ; décision d'architecture : ADR 6 de `SOLUTION_DESIGN.md`. Les demandes de correction (Epic 5) la compléteront.

**Comportement :** `functional-specs/ws-func-05-traceability.md`.

## La table `audit_log`

- **Colonnes :**
  - `id` : numéro croissant, qui garde l'ordre exact des entrées, puisque toutes celles d'une transaction ont la même heure ;
  - `occurred_at` (UTC) ;
  - `actor_user_id` (nul pour un libellé) et `actor_label` ;
  - `subject_type` et `subject_id` : la fiche dont l'historique reçoit l'entrée ;
  - `table_name` ;
  - `action` : `create`, `update` ou `delete` ;
  - `before` et `after`, en JSONB.
- **Index :** sur la fiche (`subject_type`, `subject_id`) et sur l'heure.
- **Protection en base :** des déclencheurs PostgreSQL refusent `UPDATE`, `DELETE` et `TRUNCATE` sur `audit_log` (migration `bb45920184ad`). Le journal ne peut donc **jamais être vidé**, même pour les tests : ceux-ci ne regardent que les entrées qu'ils ont créées.

## La capture (`app/dal/dal_audit.py`)

- **Où :** l'événement `before_flush` de SQLAlchemy. Les entrées s'ajoutent à la session de l'écriture, donc **dans la même transaction**.
- **L'auteur :** `acting_as(EntAuditActor(...))`, un `ContextVar`, que la BLL ouvre autour de chaque opération. Les libellés sont dans `app/entities/ent_audit.py` (`COMMAND_LINE_LABEL`, `PASSWORD_LINK_LABEL`, `SIGNED_IN_LABEL`, `AUTO_BLOCK_LABEL`).
  - Une écriture journalisée **sans** auteur lève `MissingAuditActorError` : c'est un oubli de code, pas un cas normal.
- **Un ordre toujours le même**, puisque SQLAlchemy n'en garantit aucun : les retraits, puis les modifications, puis les ajouts. À l'intérieur, l'ordre est celui des tables (`Base.metadata.sorted_tables`, un compte avant ses rôles), puis celui de l'identifiant.
- **Les identifiants** des fiches nouvelles sont attribués avant le flush, pour que l'entrée nomme la fiche créée.
- **Les clés étrangères données par un objet** (`UserRoleModel(user=…)`, `CourseDocumentModel(module=…)`) sont recopiées dans leur colonne avant la photo (`_fill_foreign_keys`). SQLAlchemy ne les remplit qu'à l'écriture : sans cela, l'entrée de création gardait la clé **vide**. Constaté sur US-012 (`module_id` des documents) ; cela touchait aussi, depuis US-003, `user_id` des rôles créés avec leur compte. Les entrées écrites avant la correction restent telles quelles.
- **Limite connue :** les mises à jour « en bloc » (`update(...)`, `delete(...)` exécutés directement) **échappent** au mécanisme. Elles sont proscrites sur une table journalisée (`backend/README.md` § Journal). C'est pourquoi `use_password_token` et `set_roles` (qui retire et ajoute les rôles un par un) sont écrits en opérations ordinaires.
  - Les mises à jour en bloc restent permises sur les tables exemptées, comme `close_user_sessions` sur `auth_sessions`.

## Brancher une table

Chaque modèle déclare **l'un ou l'autre** :
- `__audit__ = AuditPolicy(subject=..., secret=..., personal=...)` :
  - `subject` rend la fiche dont l'historique reçoit l'entrée. Une fiche peut s'inscrire dans l'historique d'une autre : les rôles sous leur compte (`("users", user_id)`), les modules et les documents sous leur formation (`("trainings", …)`) ;
  - `secret` : des champs jamais recopiés, remplacés par « [secret] » ou « [secret modifié] » ;
  - `personal` : des champs gardés, mais masqués à la lecture ;
- ou une ligne dans `EXEMPT_TABLES`, **avec sa raison**.

`tests/unit/test_audit_coverage.py` échoue si une table n'est ni l'un ni l'autre ; il a été vu échouer sur une table oubliée exprès.

| Table exemptée | Raison |
|---|---|
| `audit_log` | le journal lui-même |
| `password_tokens` | liens secrets à usage unique ; le mot de passe choisi est journalisé sur le compte |
| `alembic_version` | la version du schéma, tenue par Alembic |
| `login_attempts` | les tentatives de connexion : un registre à part, qui ne se modifie pas |
| `auth_sessions` | sessions prolongées à chaque requête ; jetons secrets |

## La lecture

- **Route :** `GET /api/v1/history/{genre}/{id}`, une seule pour toutes les fiches (US-010). Les genres actuels sont `users`, `trainings`, `domains` et `subdomains`.
  - La route laisse passer tous les rôles qui lisent au moins un genre (`ANY_READER`) ; la BLL vérifie le genre demandé.
  - Les entrées sont triées par `id`.
- **Le nom de l'auteur** (`actor_name`, « Prénom Nom (badge) ») est lu dans `users` par une jointure de `DalAudit.history`. Il est donné à tout lecteur de l'historique (US-010, décision 4A).
- **`bll_history.py` :** `_READERS` dit, par genre de fiche, quels rôles voient son historique. **Chaque Epic qui ajoute une fiche avec un historique ajoute sa ligne.**
  - `_SEES_PERSONAL_DATA` (administrateur et coordonnateur) voit tout.
  - Pour les autres rôles, les champs `personal` de la table sont remplacés par « [masqué] ».
- **Aucune route n'écrit dans le journal :** un test le vérifie, en lisant les routes effectives (`tests/unit/api_routes.py` ; voir `ws-tech-01-accounts-and-access.md` § Droits pour le piège de FastAPI).
- **Frontend :** l'entité commune `entities/history` (US-010).
  - `describeEntry(entry, names)` traduit une entrée en phrase, table par table : comptes, rôles, formations, domaines, sous-domaines, modules, documents.
  - `names` donne les noms connus de l'écran (formateurs, modules) ; un nom inconnu renvoie à « Détails ».
  - `HistoryPanel` affiche le panneau, sur la fiche d'un compte, d'une formation, d'un domaine ou d'un sous-domaine. Son `emptyText` dit pourquoi une fiche n'a aucune entrée.
- **Une liste chargée par une migration** (domaines et sous-domaines de départ) n'est pas au journal : la migration écrit en SQL, hors de la session.
