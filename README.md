---
created: 2026-11-09T00:00:00Z
updated: 2026-11-13T17:19:57Z
---

# CFDC — Application de gestion du centre de formation de l'AAN

**Équipe :** `jccarlbens`, `caleb17`. **Suivi :** tableau GitHub Projects « CFDC » n° 4.

Application de gestion du **Centre de Formation et de Développement des Compétences (CFDC)** de l'**Autorité Aéroportuaire Nationale (AAN)** : les **formations** et leurs **sessions**, les **formateurs**, les **modules** de formation et les **participants**, qu'ils soient **internes à l'AAN** ou **externes** (concessionnaires, etc.). L'application ne gère **aucun paiement**.

> **Statut : Epic 1 en cours** (mise en place et accès). Le socle technique est posé par US-001 ; suivi : `project-docs/execution/EPIC_EXECUTION.md`. Description complète du produit : `project-docs/PRD.md`.

Le dépôt suit la même organisation que le projet `fds-pay` : le **développement piloté par la spécification** (on documente le contexte *avant* d'écrire du code).

## Lancer l'application en local

Il faut **Docker** (avec Docker Compose). Depuis la racine du dépôt :

```bash
docker compose up --build
```

| Adresse | Ce qu'on y trouve |
|---|---|
| http://localhost:8080 | L'interface ; elle relaie `/api` vers le backend |
| http://localhost:8080/api/v1/health | L'état de l'API et de la base |
| http://localhost:8025 | Mailpit : les emails envoyés par l'application, capturés sans être envoyés |

Pour développer sans tout reconstruire : `docker compose up db`, puis le backend (`backend/README.md`) et le frontend (`frontend/README.md`) chacun dans son terminal.

## Serveur de test (Render et Neon)

> **Données fictives seulement.** Le serveur de test est public sur internet : aucun vrai participant, NIF, CIN ni téléphone n'y entre. Les vraies données n'arrivent que sur les serveurs de l'AAN.

Le serveur de test tourne sur le plan gratuit de **Render**, avec la base sur **Neon**. Il s'endort après 15 minutes sans visite (environ une minute pour se réveiller), et les fichiers déposés y sont perdus à chaque redémarrage.

**Mise en place, une seule fois :**
1. Sur **Neon**, créer un projet `cfdc-test` et copier son adresse de connexion (`postgresql://…`).
2. Sur **Render** : *New* → *Blueprint*, choisir ce dépôt. Render lit `render.yaml` et crée `cfdc-backend` et `cfdc-frontend`.
3. Dans `cfdc-backend` → *Environment*, coller l'adresse Neon dans `DATABASE_URL`.
4. Vérifier l'adresse donnée à `cfdc-backend`. Si ce n'est pas `https://cfdc-backend.onrender.com`, corriger `BACKEND_URL` dans `render.yaml` et dans `cfdc-frontend` → *Environment*.

Ensuite, chaque fusion sur `main` redéploie les deux services. Le serveur de test se vérifie sur `https://cfdc-frontend.onrender.com` (ou l'adresse que Render a donnée).

## Protéger la branche `main`, une seule fois

Sur GitHub : *Settings* → *Branches* → *Add branch ruleset* (ou *Add rule*) pour `main` :
- *Require a pull request before merging*, avec **1 approbation** ;
- *Require status checks to pass*, avec les jobs **`backend`**, **`frontend`** et **`images`** du workflow CI.

**Vérifiez que les trois noms apparaissent bien** sous *Require status checks to pass* : la case cochée seule ne suffit pas. Sans eux, une pull request à la CI rouge reste fusionnable dès qu'elle est approuvée (constaté sur la pull request n° 9).

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
├── backend/                         <- l'API FastAPI (voir backend/README.md)
├── frontend/                        <- l'interface React (voir frontend/README.md)
├── docker-compose.yml               <- toute l'application en local
├── render.yaml                      <- le serveur de test sur Render
├── .github/workflows/ci.yml         <- tests et contrôles à chaque pull request
├── .githooks/                       <- pre-commit : estampille `updated:`
└── .claude/skills/                  <- compétences Claude Code (voir plus bas)
```

**Règle unique :** `project-docs/` contient tous les documents qui parlent de *construire* le projet, et rien qui *soit* le produit. Le code vit dans `backend/` et `frontend/`.

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
