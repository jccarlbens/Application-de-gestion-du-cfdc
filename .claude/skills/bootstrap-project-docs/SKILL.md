---
name: bootstrap-project-docs
description: Interroger l'utilisateur section par section pour remplir les documents fondateurs du projet (PRD.md, NFR.md, SOLUTION_DESIGN.md, PLAN.md, GLOSSARY.md, project-docs/PROJECT_WORKFLOW.md), en utilisant les questions de réflexion déjà présentes dans chaque fichier. À utiliser quand un document contient encore des espaces réservés « (À écrire) » et des questions au lieu de contenu réel. Interview the user section by section to fill in the project's foundational documents.
created: 2026-09-08T17:38:40Z
updated: 2026-11-09T17:14:13Z
---

# Amorcer les documents du projet

## Ce que fait cette compétence

Elle guide l'utilisateur à travers chaque document fondateur du projet, une section à la fois, en se servant des questions de réflexion déjà écrites dans chaque fichier (marquées par des citations `>`). Le but est que l'utilisateur réponde aux questions et que le contenu reste le sien — et non un paragraphe plausible que l'agent aurait inventé à sa place.

**Répondez à l'utilisateur en français.** Ce kit est la version française ; sa prose est en français et ses chemins de fichiers ne le sont pas.

## Ordre à suivre

Les documents dépendent les uns des autres — ne sautez pas d'étape. Notez que `GLOSSARY.md` n'est délibérément **pas premier** : sans savoir encore ce qu'est le produit, il n'y a aucun moyen de savoir quels termes méritent une entrée.

1. `PRD.md` — quoi, pour qui, pourquoi. **Le premier document**, ne dépend de rien.
2. `NFR.md` — le niveau de qualité (peut se faire en parallèle du PRD, pas avant lui)
3. `SOLUTION_DESIGN.md` — comment c'est construit ; exige que le PRD et le NFR existent d'abord
4. `PLAN.md` — le séquencement ; exige les identifiants de Workstream venant de `SOLUTION_DESIGN.md`
5. `GLOSSARY.md` — peut commencer dès qu'un premier brouillon de PRD existe (les premiers termes émergent), mais à ne **finaliser** qu'une fois `PLAN.md` terminé : c'est là qu'il y a assez de matière pour savoir quel vocabulaire compte vraiment. Sa section « Workstream, Epic, Milestone » est générique et déjà remplie dès le premier jour ; le reste est propre au produit et vient en dernier.
6. `project-docs/PROJECT_WORKFLOW.md` — le tissu conjonctif ; exige tout ce qui précède

`AGENTS.md` et `CLAUDE.md` ne font **pas** partie de ce parcours — ils se construisent en dernier, une fois les documents ci-dessus réels, comme un résumé dérivé. N'essayez pas de les rédiger pendant cet entretien.

`project-docs/execution/EPIC_EXECUTION.md`, `project-docs/functional-specs/`, `project-docs/technical-specs/` et `project-docs/execution/*` ne se rédigent **pas** non plus par réflexion — ils se remplissent plus tard, de façon incrémentale, une fois qu'un travail réel existe. N'essayez pas de les préremplir maintenant.

Quand viennent `SOLUTION_DESIGN.md` §4 / §5 / §6 (carte des composants, pile technique, couche de données), renvoyez vers **`project-docs/_ARCHITECTURE_EXPLAINED.md`** : il porte une structure backend en couches établie, une architecture frontend, les conventions de nommage et une pile recommandée, chacune avec son raisonnement et son coût. C'est un point de départ à accepter ou à rejeter délibérément, **et non un défaut à appliquer en silence** ; un service utilitaire à un seul point d'entrée ne doit pas y être forcé. `project-docs/learnings/03-backend-layered-architecture-template.md` porte le raisonnement long de la moitié backend.

## Règles

1. **Une section à la fois.** Ne collez pas toutes les questions de tous les documents dans un seul message — l'utilisateur ne peut pas y répondre. Choisissez la prochaine section sans réponse, posez ses questions, arrêtez-vous, attendez.
2. **N'inventez jamais une réponse à la place de l'utilisateur**, même plausible. S'il semble bloqué, proposez d'en discuter en posant une question de relance plus étroite — et non en proposant une prose finie qu'il n'aurait qu'à approuver.
3. **Ne rédigez qu'après qu'il a répondu.** Une fois que l'utilisateur a réellement répondu aux questions d'une section, écrivez le contenu de cette section à partir de ses réponses, montrez-le-lui, et demandez si c'est exact avant de passer à la suivante.
4. **Sections conditionnelles** : plusieurs sections de `PRD.md` et de `SOLUTION_DESIGN.md` sont marquées *Conditionnelle* avec une supposition préremplie. Confirmez cette supposition explicitement avec l'utilisateur plutôt que de l'accepter ou de l'écraser en silence. « À sauter, non applicable » est une réponse valable et complète pour une section conditionnelle — n'insistez pas pour obtenir un contenu qui ne s'applique pas.
5. **Ne forcez pas dans ce processus les documents véritablement incrémentaux.** `project-docs/functional-specs/` et `project-docs/technical-specs/` n'ont pas de gabarit figé, et c'est exprès — voir leur propre `README.md`. S'il vous est demandé de les amorcer maintenant, faites remarquer que rien n'a encore été livré, donc qu'il n'y a rien de réel à documenter.
6. **Arrêtez-vous et demandez avant de créer un fichier qui n'est pas déjà prévu** dans ce dépôt — n'inventez pas de nouveaux documents hors de la structure de ce kit sans vérifier d'abord.
7. **Si l'utilisateur donne une réponse qui contredit quelque chose déjà écrit** dans un document antérieur (par exemple une décision du PRD qui change ce que disait `GLOSSARY.md`), signalez le conflit explicitement plutôt que de modifier le fichier antérieur en silence.

## Où la structure elle-même est expliquée

Si l'utilisateur demande *pourquoi* la structure a cette forme (ordre des dépendances, conventions de nommage, la couche `.claude/`, `CLAUDE.md` contre `AGENTS.md`), ne le re-dérivez pas — renvoyez vers `project-docs/learnings/01-documentation-structure-template.md` (la méthodologie complète) et son annexe `project-docs/learnings/02-document-section-reflection-questions.md` (les questions de réflexion section par section, autonome).

Pour la structure du **code** — couches backend, architecture frontend, conventions de nommage, pile recommandée — renvoyez vers `project-docs/_ARCHITECTURE_EXPLAINED.md`, et vers `project-docs/learnings/03-backend-layered-architecture-template.md` pour le raisonnement long du backend.
