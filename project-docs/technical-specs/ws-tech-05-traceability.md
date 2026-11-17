---
created: 2026-11-17T00:00:00Z
updated: 2026-11-17T17:29:48Z
---

# WS-05 — Corrections et traçabilité : implémentation

**Répond à :** comment le journal est-il construit, et comment une nouvelle table s'y branche-t-elle ?

> **Où commence cette spécification.** Elle ne couvre que **le journal**, construit par l'Epic 1 (US-003) ; décision d'architecture : ADR 6 de `SOLUTION_DESIGN.md`. Les demandes de correction (Epic 5) la compléteront.

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
- **Limite connue :** les mises à jour « en bloc » (`update(...)`, `delete(...)` exécutés directement) **échappent** au mécanisme. Elles sont proscrites sur une table journalisée (`backend/README.md` § Journal). C'est pourquoi `use_password_token` et `set_roles` (qui retire et ajoute les rôles un par un) sont écrits en opérations ordinaires.
  - Les mises à jour en bloc restent permises sur les tables exemptées, comme `close_user_sessions` sur `auth_sessions`.

## Brancher une table

Chaque modèle déclare **l'un ou l'autre** :
- `__audit__ = AuditPolicy(subject=..., secret=..., personal=...)` :
  - `subject` rend la fiche dont l'historique reçoit l'entrée (les rôles se journalisent sous leur compte : `("users", user_id)`) ;
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

- **Route :** `GET /api/v1/history/users/{id}`, `require_roles(administrateur, coordonnateur)`. Les entrées sont triées par `id`.
- **`bll_history.py` :** `_READERS` dit, par genre de fiche, quels rôles voient son historique. **Chaque Epic qui ajoute une fiche avec un historique ajoute sa ligne.**
  - `_SEES_PERSONAL_DATA` (administrateur et coordonnateur) voit tout.
  - Pour les autres rôles, les champs `personal` de la table sont remplacés par « [masqué] ».
- **Aucune route n'écrit dans le journal :** un test le vérifie, en lisant les routes effectives (`tests/unit/api_routes.py` ; voir `ws-tech-01-accounts-and-access.md` § Droits pour le piège de FastAPI).
- **Frontend :** `describeEntry` (`entities/account`) traduit une entrée en phrase ; le panneau « Historique » de la page d'un compte l'affiche.
