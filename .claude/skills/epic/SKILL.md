---
name: epic
description: Créer, affiner ou clôturer un Epic de ce projet — le pendant au niveau Epic de la compétence user-story. La création monte un nouvel Epic (dossier, PLAN.md, EPIC_EXECUTION.md, Milestone GitHub, confirmation du Workstream). L'affinage fait le cadrage et l'analyse avant construction sur le lot complet de user stories d'un Epic, avant que celles-ci ne soient créées. La clôture exécute la consolidation complète de fin d'Epic : document de clôture, paire de spécifications fonctionnelle et technique, contrôle d'obsolescence de PRD.md et SOLUTION_DESIGN.md, fermeture du Milestone GitHub. À utiliser dès qu'on demande de démarrer un nouvel Epic, de cadrer ses user stories avant de les créer, ou de clore et terminer un Epic. Create, refine, or close an Epic.
created: 2026-09-08T17:38:40Z
updated: 2026-11-09T17:14:13Z
---

# Compétence : Epic

> **Réglage, une fois, avant la première utilisation :** remplacez `[OWNER]/[REPO]` ci-dessous par vos véritables `owner/repo` GitHub. Si vous n'utilisez pas les Milestones GitHub, adaptez les étapes GitHub des procédures de création et de clôture à l'outil de suivi que nomme `project-docs/PROJECT_WORKFLOW.md` § Suivi du travail. **`CLAUDE.md` porte cette décision** — lisez-la là.

## 1. Vue d'ensemble

Autonome, dans le même esprit que `user-story` : porte sa propre copie du format utile pour ne pas avoir besoin de `project-docs/PROJECT_WORKFLOW.md` ouvert pour s'exécuter. Si ce fichier et le contenu réel de `PLAN.md` ou d'`EPIC_EXECUTION.md` se contredisent un jour, prenez les vrais fichiers comme arbitre et corrigez celui qui est obsolète.

Vocabulaire : `GLOSSARY.md` § Workstream, Epic et Milestone. Que les Epics s'enchaînent strictement de façon séquentielle (un à la fois, jamais en parallèle) est une convention propre au projet — consultez la règle énoncée par `PLAN.md` lui-même plutôt que de le supposer. Les Epics correspondent le plus souvent à un Workstream de façon biunivoque (`SOLUTION_DESIGN.md` §2 est canonique pour les identifiants et les noms de Workstream) ; un Epic qui touche le coin d'un second Workstream est l'exception documentée, pas le cas par défaut — ne le supposez pas sans vérifier.

## 2. Formats de PLAN.md

**Ligne du tableau de la vue d'ensemble des Epics** (`PLAN.md`, en haut du fichier) :
```
| **Epic N** | Nom — brève description | WS-NN | <émoji de statut + texte> |
```
Valeurs de statut employées : `⏳ Pas démarré`, `🟡 En cours — …`, `✅ Terminé — clos le AAAA-MM-JJ, voir project-docs/execution/EPIC_EXECUTION.md`.

**Section de détail d'un Epic** (`PLAN.md`, une par Epic, dans l'ordre des Epics) :
```markdown
## Epic N — Nom

**Workstream :** WS-NN Nom
**Objectif :** [une ou deux phrases — ce qui est vrai une fois cet Epic terminé]

[1 à 2 paragraphes : pourquoi cet Epic existe, ce qu'il couvre, en renvoyant à
project-docs/functional-specs/ws-func-NN-*.md et à
project-docs/technical-specs/ws-tech-NN-*.md pour le détail du comportement et
de l'implémentation, plutôt qu'en le répétant ici]

---
```

## 3. Format d'EPIC_EXECUTION.md

Une section par Epic, dans l'ordre des Epics :
```markdown
## Epic N — Nom

**Workstream :** WS-NN Nom
**Statut :** [émoji + texte, reflète la ligne de la vue d'ensemble de PLAN.md]

[1 paragraphe : le périmètre, en renvoyant à la paire de spécifications
fonctionnelle et technique]

[Facultatif : une note d'ordre de construction respectant les dépendances, si
les identifiants de user story ne correspondent pas à l'ordre dans lequel
elles doivent être construites]

| User story | Titre | Statut | Spec |
|---|---|---|---|
| US-NNN | … | 🔲 À faire | [US-NNN.md](epic-NNN-slug/US-NNN.md) |

---
```

## 4. Format du document de clôture d'Epic

`project-docs/execution/epic-NNN-slug/epic-NNN-closeout.md`.

**Dès que vous en avez écrit un, il devient le précédent — lisez le document de clôture de l'Epic précédent avant d'écrire le suivant.** Le gabarit ci-dessous laisse plusieurs choses ouvertes exprès (comment consigner un Epic qui a grossi en cours de route, comment consigner un élément resté en suspens par décision plutôt que par omission), et la réponse à chacune est plus facile à copier qu'à re-dériver.
```markdown
# Clôture de l'Epic NNN — Nom

**Workstream :** WS-NN Nom
**Statut :** ✅ Terminé — clos le AAAA-MM-JJ
**Objectif :** [la même ligne d'objectif que la section de détail de PLAN.md]

Registre figé de ce que cet Epic a livré. Le détail complet, user story par
user story, vit dans project-docs/execution/EPIC_EXECUTION.md et dans le
fichier de spécification de chacune — non dupliqué ici. Le comportement et
l'implémentation, consolidés sur l'ensemble des N user stories, sont extraits
vers project-docs/functional-specs/ws-func-NN-*.md et
project-docs/technical-specs/ws-tech-NN-*.md.

## User stories livrées

| User story | Titre | Spec |
|---|---|---|
| US-NNN | … | [US-NNN.md](US-NNN.md) |

Les N user stories sont ✅ Terminé.

## Scindé vers le non planifié

[Tableau des user stories délibérément sorties sans Milestone pour que l'Epic
puisse se clore sans elles, s'il y en a — omettez cette section s'il n'y en a
aucune.]

## Suivi

[Si le projet utilise les Milestones : « Milestone "Epic N — Nom" clos le
AAAA-MM-JJ, N/N issues fermées », plus toute réconciliation nécessaire. **S'il
suit le travail sous forme de fichiers, dites-le et dites que les étapes 2 et 7
ont été sautées et non oubliées** — un document de clôture simplement muet sur
deux étapes sur huit se lit, un an plus tard, comme une clôture incomplète.]

## Bilan pour l'équipe

[Le mini-rapport qui tient l'équipe au courant, en langage simple, lisible
sans connaître le code. Il se rédige à partir des notes de réalisation de
chaque user story, d'epic-NNN-refinement.md et des revues écrites pendant
l'Epic. Six points :
- **Livré :** ce qui marche maintenant, et où le voir en ligne.
- **Qui a fait quoi :** une ligne par membre, d'après les personnes assignées
  aux issues et les auteurs des pull requests (`gh issue list --milestone`,
  `gh pr list --state merged`).
- **Décisions :** les choix importants pris pendant l'Epic, avec leur raison.
- **Surprises :** ce qu'on croyait et qui s'est révélé faux (renvoi aux revues).
- **Points ouverts :** ce qui reste à faire ou a été reporté, et pourquoi.
- **Ensuite :** ce que l'Epic suivant va construire.]
```

---

## Procédure : créer un nouvel Epic

1. **Confirmer qu'il s'agit bien du prochain Epic.** Consultez la vue d'ensemble des Epics de `PLAN.md` — si les Epics de ce projet s'enchaînent de façon séquentielle, l'Epic immédiatement précédent devrait être `✅ Terminé`. S'il ne l'est pas, arrêtez-vous et demandez avant d'en créer un nouveau.
2. **Déterminer le Workstream.** Consultez le tableau des Workstreams de `SOLUTION_DESIGN.md` §2. Si cet Epic correspond à un Workstream existant et non encore livré, utilisez-le. S'il faut un Workstream véritablement nouveau, ajoutez d'abord une ligne là-bas (le prochain `WS-NN` séquentiel) — n'inventez pas une correspondance Epic-Workstream sans mettre à jour le tableau canonique.
3. **Créer le dossier** : `project-docs/execution/epic-NNN-slug/` (le slug correspond au nom de l'Epic, en kebab-case).
4. **Ajouter la ligne de vue d'ensemble et la section de détail de l'Epic à `PLAN.md`** (§2 ci-dessus), au statut `⏳ Pas démarré`, ou `🟡 En cours` si des user stories sont rédigées immédiatement après.
5. **Ajouter la section de l'Epic à `project-docs/execution/EPIC_EXECUTION.md`** (§3 ci-dessus), avec un tableau de user stories vide (ou rempli, si l'affinage a déjà eu lieu et que les user stories existent).
6. **Créer le Milestone GitHub** : `gh api repos/jccarlbens/Application-de-gestion-du-cfdc/milestones -f title="Epic N — Nom"`. Vérifiez que le titre exact correspond mot pour mot à ce qui est dans `PLAN.md` et `EPIC_EXECUTION.md` — la procédure de création de la compétence `user-story` apparie sur cette chaîne exacte.
7. **Rapporter** le numéro du nouvel Epic, le dossier, le Milestone et le Workstream, et dire si c'est l'affinage (user stories pas encore rédigées) ou la création de `user-story` (user stories prêtes) qui doit s'exécuter ensuite.

## Procédure : affiner un Epic

Cadrage au niveau de l'Epic avant que l'une de ses user stories ne soit créée — analogue à l'affinage de `user-story`, un niveau au-dessus : questions ouvertes résolues, lot de user stories planifié, dépendances cartographiées, avant qu'un seul fichier `US-NNN.md` n'existe.

1. **Établir le périmètre** : quelle capacité cet Epic livre-t-il, de bout en bout ? Demandez si ce n'est pas déjà clair à partir de la description en une ligne de l'Epic dans `PLAN.md`.
2. **Résoudre les questions ouvertes bloquantes pour la construction** — les choix techniques (bibliothèques, schéma, protocoles) sans lesquels les user stories de l'Epic ne peuvent pas être écrites. Cherchez les bonnes pratiques externes quand c'est pertinent (énoncez les constats et les sources avant de demander) ; demandez pour ce qui relève d'une préférence propre au projet. Consignez les résolutions dans `SOLUTION_DESIGN.md` (§15 Questions ouvertes, ou §14 sous forme d'ADR si c'est au niveau de l'architecture) ou dans la spécification technique du Workstream, selon celle qui existe déjà.
3. **Planifier le lot de user stories** : rédigez une liste de user stories (titre + périmètre en une ligne pour chacune) couvrant tout le périmètre de l'Epic, sans encore créer de fichiers de spécification. Identifiez les vraies dépendances entre elles.
4. **Déterminer l'ordre de construction** : si les dépendances font que l'ordre des identifiants n'est pas l'ordre de construction, établissez la séquence réelle — elle devient la note d'« ordre de construction respectant les dépendances » dans `EPIC_EXECUTION.md` (§3 ci-dessus).
5. **L'écrire dans `project-docs/execution/epic-NNN-slug/epic-NNN-refinement.md`, puis le rapporter.** Le rapport est destiné au propriétaire du projet, pour qu'il réponde ; le fichier existe pour que les réponses, les constats et les questions ouvertes survivent à une compaction et soient trouvables par une session qui n'était pas là. **Nommez ce fichier depuis la section d'Epic d'`EPIC_EXECUTION.md`**, parce que la section d'ordre de lecture de votre `AGENTS.md` y envoie une session qui reprend, et que rien d'autre ne dira comment il s'appelle.

   Il porte : les constats issus de la lecture du code source (numérotés `E<N>-<n>`, avec une colonne de statut), tout désaccord avec ce que `PLAN.md` ou une revue prédisait pour cet Epic, les questions ouvertes avec une recommandation pour chacune, et le lot de user stories dans l'ordre de construction. **Tant que l'Epic est ouvert, ce fichier est l'endroit où vivent ses règles** — l'unique exception bornée du tableau « où vit une règle » d'`AGENTS.md` — et c'est toute la raison pour laquelle c'est un fichier et non un message.

6. **Rapporter le plan** (liste des user stories + ordre de construction + questions ouvertes résolues) et obtenir confirmation avant de créer la moindre user story.
7. **Créer les user stories**, une par une, via la procédure de création de la compétence `user-story`, une fois la confirmation obtenue.

## Procédure : clôturer un Epic

Le filet de sécurité de la consolidation — exigé dès qu'un Epic s'achève, selon « Quel document mettre à jour, et quand » de `project-docs/PROJECT_WORKFLOW.md`. Chaque étape ci-dessous est réelle, pas facultative ; sauter la consolidation de la paire de spécifications ou le contrôle du PRD et de `SOLUTION_DESIGN.md` est exactement le genre de dérive que `check-project-docs` existe pour attraper plus tard — faites-le donc maintenant à la place.

```
Avancement de la clôture d'Epic :
- [ ] Étape 1 : confirmer que chaque user story est réellement terminée
- [ ] Étape 2 : réconcilier l'état des issues et du Milestone GitHub
- [ ] Étape 3 : écrire le document de clôture
- [ ] Étape 4 : consolider la paire de spécifications fonctionnelle et technique, et déplacer chaque règle hors d'epic-NNN-refinement.md
- [ ] Étape 5 : vérifier l'obsolescence de PRD.md et SOLUTION_DESIGN.md
- [ ] Étape 6 : mettre à jour EPIC_EXECUTION.md et PLAN.md
- [ ] Étape 7 : fermer le Milestone GitHub
- [ ] Étape 8 : rapporter
```

**Étape 1 — Confirmer que chaque user story est réellement terminée.** Chaque ligne du tableau de cet Epic dans `EPIC_EXECUTION.md` devrait être `✅ Terminé`. Si certaines ne le sont pas et que le propriétaire du projet veut quand même clore (par exemple en scindant une traînarde vers le non planifié), confirmez explicitement quelles user stories sont sorties et pourquoi avant de continuer.

**Étape 2 — Réconcilier l'état des issues et du Milestone GitHub.** `gh api repos/jccarlbens/Application-de-gestion-du-cfdc/milestones/<N>` et vérifiez que `open_issues == 0`. Une user story marquée terminée dans la spécification mais dont l'issue est encore ouverte (cela arrive avec des fusions par PR qui ne ferment pas automatiquement) demande une réconciliation : `gh issue close <N> --comment "…"` en expliquant l'écart de tenue de registre.

**Étape 3 — Écrire le document de clôture** (§4 ci-dessus) à `project-docs/execution/epic-NNN-slug/epic-NNN-closeout.md`, **section « Bilan pour l'équipe » comprise**. Écrivez-la maintenant, pendant que tout le contexte de l'Epic est là : c'est le message que l'équipe lira.

**Étape 4 — Consolider la paire de spécifications fonctionnelle et technique.** Relisez les notes de réalisation et les décisions de chaque user story (et non seulement le tableau de synthèse du document de clôture — la vraie substance est dans le fichier de chacune). Écrivez ou mettez à jour `project-docs/functional-specs/ws-func-NN-*.md` (le comportement seulement, ce qu'un utilisateur, un visiteur ou un administrateur vit) et `project-docs/technical-specs/ws-tech-NN-*.md` (l'implémentation seulement, en renvoyant à la spécification fonctionnelle plutôt qu'en la répétant). Si l'un des deux fichiers a déjà un contenu partiel issu de mises à jour incrémentales pendant l'Epic, réconciliez plutôt que d'écraser à l'aveugle — cherchez la dérive entre ce que les user stories ont réellement construit et ce qui a été écrit en cours d'Epic.

**Videz le fichier d'affinage de ses règles, et dites où chacune est allée.** `epic-NNN-refinement.md` portait les règles de cet Epic tant qu'il était ouvert, ce qui est l'exception bornée du tableau « où vit une règle » d'`AGENTS.md`. La clôture est le moment où l'exception s'achève : chaque règle qu'il contient part vers le document qui possède les règles de son genre — généralement cette paire de spécifications, parfois `SOLUTION_DESIGN.md` sous forme d'ADR, parfois `AGENTS.md`. **Un Epic qui se clôt en laissant une règle uniquement dans son fichier d'affinage ne s'est pas clos.** Ce qui reste derrière, c'est le compte rendu : les constats, ce qui était cru, ce que la lecture du code source a falsifié. Marquez le statut du fichier comme clos et laissez-le comme l'histoire de l'Epic, à côté de son document de clôture.

**Combien de paires, quand l'Epic a touché plusieurs Workstreams.** Écrivez une paire pour le Workstream que l'Epic a **déclaré**, plus tout autre dont la contribution est un *sujet entier cohérent* plutôt qu'un coin — et consignez les contributions des Workstreams restants sous forme d'un paragraphe chacune dans le document de clôture, à la place.

La raison est qu'**une spécification existante se lit comme le compte rendu de tout son domaine, donc une spécification maigre est pire qu'une spécification absente.** Un Epic qui a touché un coin d'un autre Workstream produirait une spécification décrivant ce coin sans rien dire du reste — et la personne suivante qui l'ouvre n'a aucun moyen de savoir qu'elle est partielle. Un paragraphe dans le document de clôture ne prétend rien de tel. `project-docs/functional-specs/README.md` porte la règle.

**Dites où commence chaque spécification.** Un Workstream dont le cœur a été construit avant que la convention de user story n'existe n'a aucune note de réalisation à consolider, donc sa spécification ne couvre que ce que l'Epic qui clôt y a livré, et elle doit le dire dans un en-tête — sinon elle prétend en silence être toute l'histoire de ce Workstream.

**Étape 5 — Vérifier l'obsolescence de PRD.md et de SOLUTION_DESIGN.md.** C'est explicitement distinct de l'étape 4 : la paire de spécifications de Workstream documente le *comportement et l'implémentation* ; `PRD.md` et `SOLUTION_DESIGN.md` font des affirmations de *produit et d'architecture* qui peuvent devenir obsolètes indépendamment (un énoncé de périmètre, un diagramme de composants, une description du modèle d'accès). Relisez les sections de chacun que le domaine de cet Epic touche et demandez : quelque chose ici décrit-il encore l'état d'avant l'Epic, ou contredit-il ce qui a réellement été construit ? Rapportez les constats et obtenez confirmation avant de modifier l'un ou l'autre — tous deux sont des documents de granularité « par décision » ou « par décision d'architecture » (tableau de `PROJECT_WORKFLOW.md`), et non des documents édités couramment.

**Lisez deux choses au-delà du domaine de cet Epic, parce que limiter le contrôle au domaine est la façon dont le pire constat passe à travers.** Les constats que vous attendez sont à l'intérieur du domaine : un prérequis livré encore décrit comme en attente, une règle dépassée, une affirmation désormais vérifiée encore présentée avec prudence. Le constat coûteux, non. Sur le projet dont cette procédure est issue, le pire constat lors d'une clôture d'Epic était une section de `PRD.md` affirmant que la plupart des documents qu'elle listait n'existaient pas encore — **faux depuis deux Epics entiers**, à mille lieues du sujet de cet Epic, et une chose que rien n'aurait jamais relue sauf une procédure qui dit de le faire. Vérifiez donc aussi :

- **Toute section qui fait un inventaire ou une affirmation d'existence** — « seuls X et Y existent aujourd'hui », « pas encore construit », « prévu pour », une liste de documents liés. Celles-là deviennent obsolètes par la simple continuation du projet, sans aucune modification à proximité, et c'est pourquoi aucune user story ne les attrape jamais.
- **Tout ce que l'Epic a *livré* et qu'un document décrit encore comme un prérequis, un risque ou un travail futur.** Un Epic qui débloque quelque chose laisse presque toujours, quelque part, une phrase qui l'attend encore.

**Étape 6 — Mettre à jour `EPIC_EXECUTION.md` et `PLAN.md`.** Ligne de statut → `✅ Terminé — clos le AAAA-MM-JJ`, avec un renvoi vers le document de clôture. La ligne de vue d'ensemble et la section de détail de `PLAN.md` reçoivent le même traitement (la section de détail devient un renvoi clos).

**Étape 7 — Fermer le Milestone GitHub** : `gh api -X PATCH repos/jccarlbens/Application-de-gestion-du-cfdc/milestones/<N> -f state=closed`, seulement une fois que l'étape 2 a confirmé `open_issues == 0`.

**Étape 8 — Rapporter.** Confirmez chacune des étapes ci-dessus, signalez explicitement si l'étape 5 a trouvé dans `PRD.md` ou `SOLUTION_DESIGN.md` quelque chose demandant une modification de suivi (même si la réponse est « vérifié, rien d'obsolète »), **listez chaque règle sortie d'`epic-NNN-refinement.md` et le document dans lequel chacune a atterri** — ou dites que le fichier n'en contenait aucune — et nommez l'Epic suivant selon la vue d'ensemble des Epics de `PLAN.md`. Ne le démarrez pas ; c'est une instruction distincte et explicite.
