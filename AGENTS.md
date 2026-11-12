---
created: 2026-11-09T00:00:00Z
updated: 2026-11-12T15:53:34Z
---

# AGENTS.md — CFDC

## Ce qu'est ce projet

L'application CFDC retrace les formations que dispense l'**Autorité Aéroportuaire Nationale (AAN)** à travers son **Centre de Formation et de Développement des Compétences (CFDC)** : formations, modules, sessions, participants (internes à l'AAN ou externes), présences, notes sur 100 et remise des attestations. Elle aide aussi à planifier le calendrier des formations. Elle remplace une gestion sur papier. **Aucun paiement.** Elle est construite par deux personnes : `jccarlbens` (auteur et administrateur informatique) et `caleb17`.

**Phase actuelle :** Epic 1 (mise en place et accès) ; le socle technique est posé par US-001. Statut : `project-docs/execution/EPIC_EXECUTION.md`.

## Carte des dossiers

```text
AGENTS.md, CLAUDE.md        instructions pour les agents (ce fichier, et son import)
README.md                   présentation du dépôt
STARTER_PROMPT.md           prompt pour remplir les documents avec un agent
project-docs/
  PRD.md                    quoi, pour qui, pourquoi
  NFR.md                    niveau de qualité, risques, dépendances
  SOLUTION_DESIGN.md        architecture, Workstreams WS-NN, schéma de données, ADR
  PLAN.md                   ordre des Epics, priorisation MoSCoW
  GLOSSARY.md               le sens de chaque terme
  PROJECT_WORKFLOW.md       cycle de travail, suivi, définition du « terminé »
  _ARCHITECTURE_EXPLAINED.md  structure backend / frontend et conventions de nommage
  execution/                EPIC_EXECUTION.md, puis un dossier par Epic (US-NNN.md, refinement, closeout)
  functional-specs/, technical-specs/   une paire par Workstream, remplie à mesure des livraisons
  reviews/                  ce qui était cru, et s'est révélé faux (NN-nom.md)
  learnings/                pratiques transposables à d'autres projets (NN-nom.md)
  exploration/              notes brutes, jamais citées comme décisions
  templates/                modèle de user story
.claude/skills/             compétences : bootstrap-project-docs, epic, user-story, get-work-status…
.githooks/                  estampille `updated:` à chaque commit
backend/                    API FastAPI en couches : app/{entities,dal,bll,api/v1}, alembic/, tests/{unit,integration} ; voir backend/README.md
frontend/                   React en Feature-Sliced Design : src/{app,pages,shared}, tests/{pure,rendered}, nginx/ ; voir frontend/README.md
docker-compose.yml          toute l'application en local (db, backend, frontend, mailpit)
render.yaml                 serveur de test sur Render (données fictives seulement)
.github/workflows/ci.yml    tests et contrôles à chaque pull request
```

## Pile technique

Voir `project-docs/SOLUTION_DESIGN.md` §5 (pile), §11 (déploiement) et ses ADR. Ne la recopiez pas ici.

## Ordre de lecture pour une première session

**Reprise rapide :** `project-docs/execution/EPIC_EXECUTION.md` → `PLAN.md` § Prochaines étapes immédiates → si un Epic est ouvert, son `epic-NNN-refinement.md`. La compétence `get-work-status` fait ce parcours.

**Orientation complète :** `PRD.md` → `NFR.md` → `SOLUTION_DESIGN.md` → `PLAN.md` → `GLOSSARY.md` → `PROJECT_WORKFLOW.md`.

## Renvois — quel document est canonique pour quoi

| Sujet | Document canonique |
|---|---|
| Produit, publics, capacités, exigences fonctionnelles de haut niveau, hors périmètre | `PRD.md` |
| Comportement détaillé d'un domaine livré (le « FRD ») | `functional-specs/ws-func-NN-*.md` |
| Qualité, risques, dépendances | `NFR.md` |
| Workstreams, architecture, schéma, ADR, questions ouvertes techniques | `SOLUTION_DESIGN.md` |
| Ordre des Epics, MoSCoW, prochaine action | `PLAN.md` |
| Sens d'un terme | `GLOSSARY.md` |
| Cycle de travail, suivi, définition du « terminé » | `PROJECT_WORKFLOW.md` |
| Statut de chaque user story | `execution/EPIC_EXECUTION.md` |
| Structure du code, conventions de nommage | `_ARCHITECTURE_EXPLAINED.md` |

**Où va une règle quand un travail en produit une.** Une règle ne vit jamais uniquement dans une revue, et une revue n'est jamais une lecture obligatoire pour faire le travail.

| Ce que le constat s'est révélé être | Où va la règle |
|---|---|
| ce qu'est le produit, ou pour qui il est | `PRD.md` |
| un niveau de qualité, un risque, une dépendance | `NFR.md` |
| une décision ou une contrainte d'architecture | `SOLUTION_DESIGN.md`, sous forme d'ADR |
| notre façon de travailler, ou ce que « terminé » veut dire | `PROJECT_WORKFLOW.md` |
| comment un Workstream se comporte / est construit | sa paire de specs fonctionnelle / technique |
| ce que veut dire un mot | `GLOSSARY.md` |
| quelque chose qu'aucune session ne doit rater | ce fichier |
| une pratique transposable à un autre projet | `learnings/` |
| rien au-delà de la correction elle-même | cela reste dans la revue |

**Seule exception : le travail en cours.** Tant qu'un Epic est ouvert, ses règles et questions ouvertes vivent dans `project-docs/execution/epic-NNN-*/epic-NNN-refinement.md`. À la clôture, elles déménagent.

## Conventions

- **Langue :** la prose est en français ; les chemins, les noms de fichiers et tous les identifiants de code sont en anglais.
- **Dossiers historiques** (`reviews/`, `learnings/`) : fichiers `NN-nom.md`, numéro attribué une fois et jamais réattribué. Les exemples `learnings/01`–`03` viennent du kit ; les nôtres commencent à `04`.
- **Frontmatter :** chaque fichier markdown porte `created` et `updated` en UTC ; `updated` est estampillé par `.githooks/pre-commit`, jamais à la main.
- **Pas d'invention :** l'agent ne remplit jamais un document fondateur à la place de l'équipe ; il pose les questions, attend la réponse, puis rédige.
- **Epics séquentiels.** Un seul Epic actif à la fois, dans l'ordre de `PLAN.md` ; les deux membres travaillent en parallèle sur des user stories différentes.
- **Suivi sur GitHub.** User story = issue, Epic = Milestone, tableau Projects « CFDC » n° 4. L'agent ne déplace jamais une issue sur le tableau et ne marque jamais une user story comme terminée de lui-même. Détail : `project-docs/PROJECT_WORKFLOW.md`.
- **Le serveur décide des droits.** Chaque action est vérifiée côté serveur selon le tableau de `PRD.md` §5 ; masquer un bouton ne suffit jamais.
- **Rien ne s'efface sans trace.** Toute modification et toute suppression passe par le journal (qui, quoi, quand, avant, après) ; une information enregistrée ne se modifie ou ne se supprime que par une demande de correction validée par l'administrateur (`PRD.md` §7).
- **Attention aux homonymes** : session de formation / session de connexion, demande de formation / demande de correction, chef de service du CFDC / chef du service demandeur (`GLOSSARY.md`).
- **Base de données :** tables et champs en anglais, noms de tables au pluriel en `snake_case` ; horodatages en UTC (ISO-8601 avec `Z`), convertis en heure locale dans l'interface seulement.

## Confidentialité

Les **données personnelles des participants** (NIF, CIN, téléphone) ne sont visibles, une fois saisies, que du **coordonnateur** et de l'**administrateur informatique**. Le formateur ne voit que les noms de ses participants. L'application reste sur le réseau interne de l'AAN. Détail : `PRD.md` §5 et §7, `NFR.md` § Sécurité.
