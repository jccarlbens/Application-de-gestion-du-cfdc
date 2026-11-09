---
name: get-work-status
description: Rapporte l'état courant du projet — l'Epic en cours, la dernière user story terminée, toute user story en cours, la prochaine à construire selon l'ordre des dépendances, et ce que reportent les Prochaines étapes immédiates de PLAN.md. En lecture seule, ne modifie rien. À utiliser au début d'une session pour reprendre vite, ou quand on demande « où en sommes-nous », « et après », « quel est le statut ». Reports current project status, read-only.
created: 2026-09-08T17:38:40Z
updated: 2026-11-09T17:14:13Z
---

# Compétence : état du travail

En lecture seule, et ne modifie rien — si elle trouve une dérive, elle la rapporte. Elle automatise l'ordre de lecture de **reprise rapide** de votre `AGENTS.md`, pour qu'il n'ait pas à être exécuté à la main et que ses étapes restent identiques à chaque fois. Cette section est canonique pour l'ordre ; si cette compétence et elle se contredisent un jour, `AGENTS.md` l'emporte et c'est ce fichier-ci qu'on corrige.

> **La passation, ce sont les fichiers committés, pas un document de passation.** Cette compétence lit le suivi, le plan et la revue la plus récente, parce que ce sont les seules choses qu'une session qui n'était pas là peut réellement croire. Voir `prepare-compact`, dont tout le travail consiste à les garder suffisants.

## Procédure

1. **Lire `project-docs/execution/EPIC_EXECUTION.md`** — trouver l'Epic courant : celui marqué `🟡 En cours`, et son tableau de user stories.
   - **Si aucun Epic n'est `🟡 En cours`, le projet est *entre* deux Epics** et il n'y a pas de user story courante. Dites-le franchement plutôt que de rapporter le dernier Epic clos comme s'il était courant, et passez directement à l'étape 4 — entre deux Epics, `PLAN.md` § Prochaines étapes immédiates est la seule chose qui sache ce qui vient après. C'est un état normal, pas une erreur : c'est l'état qui suit immédiatement la clôture de n'importe quel Epic.
2. **Lire le tableau de la vue d'ensemble des Epics de `PLAN.md`** — vérifier par recoupement que le statut de l'Epic correspond ; sinon, signaler l'écart (c'est exactement le genre de dérive que cherche `check-project-docs`, mais un écart de statut trouvé ici vaut d'être remonté immédiatement, non différé).
3. **À partir du tableau de user stories de l'Epic courant**, identifier :
   - La **dernière user story marquée `✅ Terminé`**.
   - Toute user story **`🟡 En cours`** — il doit y en avoir **au plus une**, et deux est un constat qui vaut d'être rapporté pour lui-même. Toute user story **`⛔ Bloqué`**, avec la raison qu'elle porte. Ces quatre états sont la liste complète ; **`✅ Accepté` n'est pas un état** et une user story qui le porte est une dérive.
     > **Si votre `PROJECT_WORKFLOW.md` § Suivi du travail n'a pas encore énoncé la liste des états, c'est là qu'elle va**, et cette compétence devrait y renvoyer plutôt que de porter sa propre copie. Les quatre ci-dessus sont la liste de départ du kit.
   - La **prochaine user story à construire**, selon l'ordre de construction documenté de l'Epic respectant les dépendances (énoncé dans sa section de `EPIC_EXECUTION.md`, par exemple « US-001 → US-004 → US-002 → … ») plutôt que l'ordre brut des identifiants, si un tel ordre est documenté. S'il n'existe aucun ordre explicite, prendre la première user story `🔲 À faire` par identifiant.
4. **Lire `project-docs/PLAN.md` § Prochaines étapes immédiates.** C'est l'instruction de report du projet — ce qu'une session précédente a délibérément laissé à la suivante, et que les tableaux de user stories seuls ne montrent pas. **Vérifiez si le point 1 nomme quelque chose de déjà fait** ; un chemin de reprise dont le premier point est accompli est la forme de dérive la plus courante ici, et le rapporter est plus utile que de le suivre.
5. **Lire le fichier le plus récemment modifié de `project-docs/reviews/`** — avec `ls -t` plutôt que par nom de fichier, puisque ceux-ci sont nommés par sujet et non par date. Il porte ce qui était cru récemment et s'est révélé faux, c'est-à-dire le contexte qui a le moins de chances de survivre à une compaction.
6. **Rapporter**, dans cet ordre :
   - L'Epic courant (numéro, nom, statut).
   - La dernière user story terminée (identifiant + titre).
   - La user story en cours, s'il y en a une.
   - La prochaine user story à construire (identifiant + titre), et si elle a besoin d'un affinage (selon la compétence `user-story`) avant d'être construite.
   - **Le point 1 des prochaines étapes immédiates**, mot pour mot ou légèrement condensé — ne laissez pas tomber les précisions du genre « le schéma est arrêté, ne le rouvrez pas » — et dites s'il semble déjà fait.
   - Le sujet de la revue la plus récente, en une ligne, pour que ses corrections ne soient pas re-dérivées.
   - Tout ce qui, à l'étape 2, ne correspondait pas lors du recoupement du statut de l'Epic.

Gardez le rapport lui-même court — c'est un relevé d'état, pas une re-dérivation du projet entier. Renvoyez vers les fichiers source plutôt que de ré-expliquer tout leur contenu.
