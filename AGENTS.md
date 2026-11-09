---
created: 2026-11-09T00:00:00Z
updated: 2026-11-09T17:14:13Z
---

# AGENTS.md — CFDC

> **Statut : provisoire.** Ce fichier est le résumé *dérivé* de tous les documents de `project-docs/` ; il se complète **en dernier**, une fois `PRD.md` → `PROJECT_WORKFLOW.md` remplis. Pour l'instant, il ne porte que ce qui est déjà vrai : la carte des dossiers et les conventions.

## Ce qu'est ce projet

Application de gestion du centre de formation (CFDC) de l'AAN : formateurs, modules et participants (internes à l'AAN ou externes). Pas de paiement. *(Description complète : `project-docs/PRD.md`, à écrire.)*

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
```

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
