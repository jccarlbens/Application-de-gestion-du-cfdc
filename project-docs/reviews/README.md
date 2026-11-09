---
created: 2026-09-10T19:30:13Z
updated: 2026-11-09T17:14:13Z
---

# `reviews/` — ce que vous croyiez et qui s'est révélé faux

**Ce dossier est vide et c'est le plus précieux d'entre tous.** Rien n'y entre le premier jour, et s'il est encore vide après votre premier Epic, quelque chose a mal tourné — non pas dans le projet, mais dans la tenue du registre.

Une revue n'est pas un document de conception et pas un journal des modifications. Son mode est exactement une chose :

> voici ce que je croyais, voici la preuve que c'était faux, voici l'affirmation corrigée.

## Les règles qui la font fonctionner

**Un fichier par travail**, numéroté et nommé d'après son sujet : `01-architecture-review.md`, `02-frontend-test-review.md`. **Le numéro est l'ordre dans lequel la revue a été écrite, ni une priorité ni une catégorie** — ce dossier est un historique, donc l'ordre chronologique est celui dans lequel le lire, et un simple `ls` le trierait par sujet, ce qui n'apprend rien sur l'évolution de la compréhension. Attribuez le numéro une fois et ne le réattribuez jamais : une revue ultérieure prend le suivant, car une citation dans un vieux message de commit doit continuer de pointer vers le même document. Pas de date dans le nom de fichier — les entrées à l'intérieur en portent, et le frontmatter `updated:` aussi.

**Écrite à l'instant du constat, et non à la fin du travail.** C'est toute la règle, et la raison est arithmétique : une correction ne coûte presque rien à écrire tant qu'elle est fraîche, et devient presque impossible à reconstituer une semaine plus tard. Une revue écrite à la fin d'un Epic est un résumé de ce qui a été livré, et c'est à cela que sert le document de clôture.

**Numérotez les constats** — `F1`, `F2`, ou un tableau avec une colonne *statut*. Un constat résolu plus tard reçoit sa résolution en ajout, jamais une édition qui ferait croire que l'original avait eu raison depuis le début.

**Gardez les corrections, surtout les embarrassantes.** Une revue dont tous les constats se sont révélés *« un peu plus subtils que prévu »* est une revue que personne n'a écrite honnêtement. Le projet d'origine dont vient ce kit en a une qui consigne que son propre `README.md` affirmait que deux modules étaient couverts par des tests unitaires alors qu'aucun des deux ne l'était — découvert en tombant sur un bogue dans l'un d'eux — et ce paragraphe vaut plus que n'importe quelle prose d'architecture propre à côté de lui.

## Ce qui ne vit pas ici : les règles

**Un constat qui devient une règle ne doit pas rester uniquement dans ce dossier**, et c'est l'erreur qui vaut d'être devancée plutôt que découverte. Une revue est le *compte rendu* — ce qui était cru, la preuve, la correction. Quelqu'un qui cherche une règle ouvre le document qui possède les règles de ce genre ; personne ne pense à lire un historique pour découvrir quelles sont les règles.

Donc à la clôture du travail, chaque constat reçoit une destination : le PRD s'il a changé ce qu'est le produit, `SOLUTION_DESIGN.md` s'il a changé l'architecture, `PROJECT_WORKFLOW.md` s'il a changé votre façon de travailler, la paire de spécifications du Workstream s'il concerne un seul domaine, `AGENTS.md` si aucune session ne doit le rater, `learnings/` s'il se transpose au-delà de ce projet — et **nulle part du tout s'il n'était qu'une correction**, auquel cas la revue est déjà complète. Votre `AGENTS.md` devrait porter ce tableau ; `project-init-kit-fr/AGENTS.md` § *Où vit une règle* en donne la forme.

La revue reste exactement où elle est, et le nouveau foyer de la règle peut y renvoyer pour l'histoire complète. Rien ne renvoie dans l'autre sens.

## Pourquoi c'est séparé de `learnings/`

| | |
|---|---|
| **une revue** | contemporaine, datée, liée à *ce* code. Écrite avant que quiconque sache comment l'histoire se terminerait |
| **un apprentissage** | distillé, réutilisable, écrit après coup, destiné à s'appliquer à votre *prochain* projet |

**Une revue est la source d'où vient un apprentissage.** Plus tard, une relecture de ces fichiers demande : *est-ce que quelque chose là-dedans est vrai au-delà de cette base de code ?* Quand la réponse est oui, cela devient un fichier `learnings/` — **et la revue reste exactement où elle est.** Extraire n'est pas déplacer. Fusionner les deux dossiers perd ce qui rend une revue instructive : le fait qu'elle a été écrite depuis l'intérieur de l'erreur.

## Si vous transmettez ce projet à quelqu'un

Ce dossier est la partie de votre processus qui est aussi un produit. Un lecteur apprend davantage de la façon dont vous vous êtes trompé que de l'architecture à laquelle vous êtes arrivé, et c'est le seul endroit qui en survit.
