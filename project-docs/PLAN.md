---
created: 2026-11-09T00:00:00Z
updated: 2026-11-12T15:46:47Z
---

# PLAN.md — CFDC

**Répond à :** dans quel ordre, regroupé en quels Epics ?
**Dépend de :** `SOLUTION_DESIGN.md` pour les identifiants de Workstream.

> **Statut : V1 du plan, validée par l'utilisateur le 2026-11-10.** Aucune échéance n'est encore fixée par la direction du CFDC.

> **Rappel de vocabulaire (générique — voir aussi `GLOSSARY.md` § Workstream, Epic et Milestone) :**
> - **Epic** = *quand, et quelle quantité à la fois*. Étape de construction séquentielle et bornée dans le temps, regroupant un ou plusieurs Workstreams (définis dans `SOLUTION_DESIGN.md`). Identifiant `epic-NNN-name` (dossier à trois chiffres).
> - **User story** = l'unité concrète de travail à l'intérieur d'un Epic. Identifiant `US-NNN`, séquentiel sur tout le projet, jamais remis à zéro par Epic.
> - **Milestone** = ce qui est livré — la représentation GitHub d'un Epic, dès lors qu'un outil de suivi est utilisé.

---

## Vue d'ensemble des Epics

> 1. Dans quel ordre les domaines fonctionnels seront-ils réellement travaillés, et pourquoi cet ordre ?
> 2. Un Epic est-il bloqué par l'achèvement d'un autre ?
> 3. Deux Epics pourraient-ils véritablement avancer en parallèle, ou le séquentiel est-il réellement nécessaire ici — et pourquoi ?

| Ordre | Epic | Workstreams | Priorité | Statut |
|---|---|---|---|---|
| 1 | `epic-001-setup-and-access` — Epic 1 — Mise en place et accès | WS-01, WS-05 (journal) | Must | 🟡 En cours |
| 2 | `epic-002-trainings-and-modules` | WS-02 | Must | ⏳ Pas démarré |
| 3 | `epic-003-requests-and-sessions` | WS-03 | Must | ⏳ Pas démarré |
| 4 | `epic-004-participants-and-tracking` | WS-04 | Must | ⏳ Pas démarré |
| 5 | `epic-005-corrections` | WS-05 | Must | ⏳ Pas démarré |
| 6 | `epic-006-overview-search-export` | WS-06 | Must | ⏳ Pas démarré |

**Pourquoi cet ordre.** Chaque Epic s'appuie sur le précédent : on ne planifie pas de session sans formation, on n'inscrit pas de participant sans session, et la vue d'ensemble n'a de sens qu'une fois les données saisies. **Le journal des modifications est construit dès l'Epic 1** : chaque modification doit laisser une trace (`PRD.md` §7), et un journal ajouté à la fin laisserait échapper tout ce qui a été construit avant.

**Séquentiel, à deux.** Les Epics se suivent, un seul est actif à la fois. L'auteur et son partenaire de travail avancent **en parallèle sur des user stories différentes** de l'Epic actif.

## Tâches à accomplir — référence

Repris de `PRD.md` §4, qui reste la source.

| Rôle | Tâche à accomplir | Epics |
|---|---|---|
| Secrétaire | Tenir à jour les formations à venir et leurs participants | 2, 3, 4 |
| Coordonnateur | Avoir une vue d'ensemble de l'unité | 3, 6 |
| Chef de service du CFDC | Suivre les formations, superviser cours et formateurs, organiser les horaires | 2, 3, 6 |
| Formateur | Voir ses modules et leurs documents | 2 |
| Administrateur informatique | Jouer le rôle de sentinelle : comptes, corrections, documents | 1, 2, 5 |
| Tous | Une application simple à utiliser | tous |

> 1. Chaque tâche à accomplir correspond-elle à exactement un Epic, ou l'une d'elles s'étend-elle sur plusieurs ?

## Priorisation MoSCoW

> 1. Pour chaque tâche à accomplir, qu'est-ce qui est vraiment *Must-have* (indispensable), par opposition à *Should* (souhaitable), *Could* (possible) ou *Won't* (exclu) pour la V1 ?
> 2. Quel est le coût de s'être trompé sur quelque chose marqué indispensable et qui se révèle inutile ?
> 3. Y a-t-il quelque chose marqué exclu dont on risque quand même de vous parler — et qui vaut d'être énoncé explicitement plutôt qu'abandonné en silence ?

Il n'y a pas de MVP (`PRD.md` §11) : **toutes les capacités du PRD sont Must**, avec une exception.

| Priorité | Contenu |
|---|---|
| **Must** | Toutes les capacités de `PRD.md` §6, la double authentification **par email** comprise |
| **Should** | La double authentification **par SMS** (Digicel, Natcom). Elle dépend du budget et des opérateurs (`SOLUTION_DESIGN.md` §15, Q2) ; l'email seul suffit pour la mise en service |
| **Won't (V1)** | Le mode hors ligne, une application mobile, les comptes et convocations des participants, la génération des attestations, les notifications, les liens avec d'autres systèmes de l'AAN, l'accès depuis internet (`PRD.md` §13) |

## Détail par Epic

> **Questions à se poser, pour chaque Epic :**
> 1. Que livre cet Epic que le précédent ne livrait pas ?
> 2. Quel ou quels Workstreams touche-t-il principalement ?
> 3. Quel est l'objectif en une phrase qu'une partie prenante pourrait répéter correctement ?

### `epic-001-setup-and-access` — Must
Met en place le socle : dépôt de code, Docker Compose, GitHub Actions, serveur de test. Livre les comptes, la connexion par badge et mot de passe, la double authentification (email ; SMS en Should), les rôles, le blocage, la déconnexion automatique, et le **journal des modifications**. **Objectif :** le personnel du CFDC peut se connecter en sécurité, et toute action laisse une trace.

### `epic-002-trainings-and-modules` — Must
Livre le catalogue des formations, leurs modules et formateurs, et les documents de cours. **Objectif :** le CFDC a son catalogue de formations dans l'application, et chaque formateur y retrouve ses modules et ses documents.

### `epic-003-requests-and-sessions` — Must
Livre les demandes de formation, la planification des sessions et les horaires. **Objectif :** le coordonnateur enregistre les demandes validées et planifie les sessions dans l'application plutôt que sur papier.

### `epic-004-participants-and-tracking` — Must
Livre les participants, les inscriptions, les présences, les notes et la remise des attestations et certificats. **Objectif :** pour chaque session, on sait qui était là, avec quelle note, et qui a reçu son attestation.

### `epic-005-corrections` — Must
Livre les demandes de correction et leur validation par l'administrateur, avec l'historique visible. **Objectif :** une erreur se corrige sans jamais effacer de trace.

### `epic-006-overview-search-export` — Must
Livre la vue d'ensemble de l'unité, la recherche et l'export Excel et PDF. **Objectif :** retrouver l'historique d'une formation ou d'un participant en moins de 2 minutes, et sortir un bilan pour la direction.

## Prochaines étapes immédiates

> 1. Quelle est la toute prochaine action concrète — et non une reformulation de la feuille de route entière ?
> 2. Cette section risque-t-elle de devenir vite obsolète — le statut au quotidien devrait-il plutôt vivre dans un suivi dédié (`project-docs/execution/EPIC_EXECUTION.md`) ?

1. Finaliser `GLOSSARY.md`, puis `PROJECT_WORKFLOW.md`, puis `AGENTS.md` et `CLAUDE.md`.
2. Poser au service informatique de l'AAN les questions Q1 et Q3 de `SOLUTION_DESIGN.md` §15 (Docker, système des serveurs, sortie vers internet).
3. Créer l'Epic 1 avec la compétence `epic` (Milestone sur le tableau GitHub « CFDC » n° 4), l'affiner, puis écrire sa première user story.

---
