---
created: 2026-11-09T00:00:00Z
updated: 2026-11-09T17:14:13Z
---

# CFDC — Application de gestion du centre de formation de l'AAN

Application de gestion du centre de formation (CFDC) de l'AAN : les **formateurs**, les **modules** de formation et les **participants**, qu'ils soient **internes à l'AAN** ou **externes** (concessionnaires, etc.). L'application ne gère **aucun paiement**.

> **Statut : phase de cadrage.** Aucune ligne de code n'existe encore. Les documents de `project-docs/` sont des structures de départ, avec leurs questions de réflexion ; ils se remplissent dans l'ordre ci-dessous, avant d'écrire du code. Description complète du produit : `project-docs/PRD.md` (à écrire).

Le dépôt suit la même organisation que le projet `fds-pay` : le **développement piloté par la spécification** (on documente le contexte *avant* d'écrire du code).

## Mise en route, une fois par clone

```bash
git config core.hooksPath .githooks
```

Ce hook estampille `updated:` sur chaque fichier markdown committé. Il a besoin de Python 3.8 ou plus ; s'il n'en trouve pas, il avertit et laisse passer le commit.

## Organisation du dépôt

```text
.
├── README.md                        <- ce fichier
├── AGENTS.md / CLAUDE.md            <- instructions pour les agents ; complétés en dernier
├── STARTER_PROMPT.md                <- le prompt pour remplir les documents avec un agent
├── project-docs/                    <- TOUS les documents sur la construction du projet
│   ├── _ARCHITECTURE_EXPLAINED.md   <- 0. à lire d'abord : comment le code sera découpé, et pourquoi
│   ├── PRD.md                       <- 1. quoi, pour qui, pourquoi (exigences produit)
│   ├── NFR.md                       <- 2. exigences non fonctionnelles : qualité, risques, dépendances
│   ├── SOLUTION_DESIGN.md           <- 3. architecture, Workstreams, données, ADR
│   ├── PLAN.md                      <- 4. ordre des Epics, priorisation MoSCoW
│   ├── GLOSSARY.md                  <- 5. le vocabulaire — finalisé en dernier
│   ├── PROJECT_WORKFLOW.md          <- 6. quel document toucher, et quand
│   ├── templates/user-story.md      <- à copier pour chaque user story
│   ├── execution/                   <- EPIC_EXECUTION.md, puis un dossier par Epic
│   ├── functional-specs/            <- le comportement de chaque domaine livré (le « FRD »)
│   ├── technical-specs/             <- l'implémentation de chaque domaine livré
│   ├── reviews/                     <- ce que l'on croyait et qui s'est révélé faux
│   ├── learnings/                   <- pratiques transposables (01–03 : exemples du kit)
│   └── exploration/                 <- recherche brute, jamais citée comme décision
├── .githooks/                       <- pre-commit : estampille `updated:`
└── .claude/skills/                  <- compétences Claude Code (voir plus bas)
```

**Règle unique :** `project-docs/` contient tous les documents qui parlent de *construire* le projet, et rien qui *soit* le produit. Le code viendra dans `backend/` et `frontend/`, générés plus tard par les compétences `scaffold-*`.

### Où sont les exigences fonctionnelles (le « FRD »)

Comme dans `fds-pay`, il n'y a pas de fichier FRD séparé :
- les **capacités** du produit (ce qu'un utilisateur peut faire) sont listées dans `PRD.md` §6, et ce qu'il ne doit jamais faire au §7 ;
- le **comportement détaillé** de chaque domaine s'écrit dans `project-docs/functional-specs/ws-func-NN-*.md`, Workstream par Workstream, à mesure que les fonctionnalités sont livrées ;
- les **critères d'acceptation** de chaque unité de travail sont dans les user stories (`execution/epic-NNN-*/US-NNN.md`).

## L'ordre de remplissage

```text
PRD.md  →  NFR.md  →  SOLUTION_DESIGN.md  →  PLAN.md  →  GLOSSARY.md  →  PROJECT_WORKFLOW.md
```

Puis `AGENTS.md` / `CLAUDE.md` (résumés de tout ce qui précède), puis le premier Epic, puis la première user story, et **seulement ensuite** la structure du code.

Le glossaire n'est pas premier : sans savoir encore ce qu'est le produit, on ne sait pas quels termes méritent une entrée. Il commence à se remplir dès le premier brouillon du PRD, mais ne se finalise qu'après `PLAN.md`.

## Les compétences Claude Code

| Compétence | Pour... |
|---|---|
| `bootstrap-project-docs` | Vous interroger section par section pour remplir les six documents fondateurs. |
| `epic` | Créer, affiner ou clôturer un Epic. |
| `user-story` | Créer, affiner, mettre à jour ou supprimer une user story (+ son issue GitHub). |
| `get-work-status` | Dire où en est le projet, en lecture seule. |
| `check-project-docs` | Auditer les documents fondateurs à la recherche de dérive. |
| `document-learning` | Écrire un fichier `project-docs/learnings/`. |
| `prepare-compact` | Reporter le travail d'une session dans les fichiers committés. |
| `scaffold-backend-service` | Générer un service FastAPI + SQLAlchemy en couches (une fois les documents écrits). |
| `scaffold-frontend-app` | Générer un frontend React + TypeScript (Feature-Sliced Design). |

**Pourquoi cette forme :** `project-docs/learnings/01-documentation-structure-template.md` pour la documentation, `project-docs/_ARCHITECTURE_EXPLAINED.md` pour le code.
