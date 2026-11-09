---
name: prepare-compact
description: Prépare une session à la compaction en faisant des fichiers committés du projet une passation suffisante — en poussant le vrai travail de la session dans les fichiers de user story, de suivi et de revue, puis en vérifiant que le chemin de reprise documenté nomme bien la prochaine action. NE lance PAS la compaction (c'est un /compact distinct, déclenché par l'utilisateur). À utiliser quand on demande de préparer une compaction, de clore une session, ou d'écrire une passation. Prepares a session for compaction.
created: 2026-09-08T17:38:40Z
updated: 2026-11-09T17:14:13Z
---

# Compétence : préparer une compaction

**La passation, ce sont les fichiers committés, et non un document de passation séparé.** Une compaction écrit son propre résumé de la conversation ; ce qu'elle ne peut pas faire, c'est rendre le *dépôt* honnête. Le travail de cette compétence est donc de laisser l'arbre dans un état où une session ayant perdu chaque mot de cette conversation peut reprendre à partir du seul ordre de lecture d'`AGENTS.md`.

> **Pourquoi aucun fichier de passation.** Une version antérieure de cette compétence écrivait deux notes ignorées par git dans un dossier de brouillon. Quand une vraie compaction est arrivée, le geste utile s'est révélé différent : pousser le travail de la session dans les fichiers suivis, pointer `PLAN.md § Prochaines étapes immédiates` vers la véritable prochaine action, et compacter. La reprise a été propre, et c'est le seul test qui compte — et contrairement à une note de brouillon, c'est versionné et c'est lu par tout le monde. **Si votre projet tient malgré tout un dossier de passation, substituez votre propre étape d'écriture de fichier à l'étape 4 ci-dessous** ; le reste s'applique sans changement.

## Procédure

**Étape 1 — Pousser le vrai travail de cette session dans le registre durable, avant toute autre chose.** C'est tout l'objet de cette compétence. Les documents de suivi sont censés être mis à jour au fil du travail (`project-docs/PROJECT_WORKFLOW.md` § « Quel document mettre à jour, et quand »), et une compaction n'est pas un endroit où stocker ce qui aurait dû être écrit. Vérifiez chacun des points suivants :

- **Une user story travaillée pendant cette session dont les `## Notes de réalisation` ne le reflètent pas encore.** Les progrès et les décisions réels appartiennent au fichier de spécification même quand la user story n'est pas prête à être terminée — procédure de mise à jour de `user-story`. Seul le propriétaire du projet marque une user story comme terminée.
- **`project-docs/execution/EPIC_EXECUTION.md`** — un statut ou une note d'ordre de construction qui a changé en cours de session.
- **`project-docs/PLAN.md`** — une ligne de statut d'Epic, ou une question ouverte résolue.
- **Une correction qui appartient à `project-docs/reviews/`** — quelque chose qui était cru au début de cette session et s'est révélé faux. La règle de `reviews/README.md` est que ces fichiers sont écrits *à l'instant du constat*, et la raison est arithmétique : cela ne coûte presque rien tant que c'est frais et c'est presque impossible à reconstituer plus tard. **Une compaction qui est sur le point de jeter la conversation est le dernier instant.**
- **Une pratique transposable qui appartient à `project-docs/learnings/`** — une habitude qui aiderait sur n'importe quel projet, pas seulement celui-ci. Voir `document-learning`.

Si l'un de ces points est en attente, **faites-le maintenant.** Ne le laissez pas comme un « reprendre ici » à moins que le propriétaire du projet ne demande de le différer. Demandez s'il n'est pas clair que quelque chose atteint ce niveau.

**Étape 2 — Obtenir la vraie date depuis l'horloge du shell.** Jamais depuis le contexte de la conversation ; une session peut s'étaler sur un temps réel important.

**Étape 3 — Vérifier l'arbre, et dire ce que vous trouvez.** `git status --short` et `git log --oneline -1`. Du travail non committé n'est pas automatiquement une erreur, mais une session fraîche a besoin de savoir si l'arbre est propre, sale délibérément, ou sale par accident. **Vérifiez aussi `git stash list`** — un stash oublié survit à une compaction et est invisible pour une session qui ne pense pas à regarder.

**Étape 4 — Vérifier que le chemin de reprise aboutit réellement quelque part d'utile.** Lisez ce que la section d'ordre de lecture d'`AGENTS.md` fait lire à une session fraîche, dans l'ordre, et confirmez que chaque élément dit encore quelque chose de vrai :

- `project-docs/execution/EPIC_EXECUTION.md` — le tableau des user stories est-il vrai *à l'instant* ?
- `project-docs/PLAN.md § Prochaines étapes immédiates` — **le point 1 nomme-t-il la prochaine action, ou celle qui vient d'être achevée ?** C'est l'étape qui échoue le plus souvent et celle qui compte le plus : un chemin de reprise dont le premier point est déjà fait envoie la session suivante re-dériver quoi faire.
- le fichier le plus récemment modifié de `project-docs/reviews/`.

Corrigez tout ce qui est obsolète. C'est le substitut d'un document de passation, et c'en est un meilleur, parce qu'il est committé et versionné.

**Étape 5 — Rapporter** ce que l'étape 1 a sauvé, l'état de l'arbre de l'étape 3, et où l'étape 4 laisse une session fraîche. Puis arrêtez-vous. **Ne lancez pas `/compact`** — c'est l'action du propriétaire du projet, et cette compétence ne fait que la préparer.
