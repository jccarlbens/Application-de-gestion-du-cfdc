---
created: 2026-09-08T17:38:40Z
updated: 2026-11-09T17:14:13Z
---

# user-story.md — gabarit de user story

> **Rappel de vocabulaire** : une **user story** est l'unité concrète de travail à l'intérieur d'un **Epic** (étape de construction séquentielle, voir `PLAN.md`), touchant un ou plusieurs **Workstreams** (domaine fonctionnel, voir `SOLUTION_DESIGN.md`). Voir aussi `GLOSSARY.md` § Workstream, Epic et Milestone.
>
> Copiez ce fichier vers `epic-NNN-<nom>/US-NNN.md` dès que le premier Epic est nommé dans `PLAN.md`. La numérotation `US-NNN` est séquentielle sur **tout le projet**, jamais remise à zéro par Epic, jamais réutilisée.

```markdown
# US-NNN : [Titre court]

**Statut :** 🔲 À faire / ✅ Terminé / etc.
**Milestone :** [nom de l'Epic]
**Dépend de :** US-XXX (facultatif — seulement s'il y a une vraie dépendance)

---

## En tant que [rôle issu de GLOSSARY.md]
Je veux [fonctionnalité ou capacité]
Afin de [résultat]

## Contexte
[Ce qui existe déjà. Dans quel état est la base de code. Sur quels fichiers,
composants ou user stories antérieures ceci s'appuie. Ce qu'il ne faut PAS
supposer déjà fait.]

## Critères d'acceptation
- [ ] [Précis et binaire]
- [ ] [...]

## Hors périmètre
- [Ce qu'il ne faut PAS construire dans cette user story]

## Tâches
- [ ] [Étape d'implémentation concrète]
- [ ] [...]

## Définition du terminé
- [ ] [Chose précise vérifiée à l'œil ou par un test]

## Notes de réalisation
[Ajoutées dès que le travail commence ou s'achève — ce qui s'est réellement
passé, les écarts par rapport au plan, les décisions prises en chemin.]
```

> **Correspondance avec la version anglaise du kit.** Les intitulés de section sont traduits, car c'est de la prose que vous rédigez ; les chemins et les identifiants ne le sont pas. Les compétences `user-story` et `epic` de ce kit emploient exactement les mêmes intitulés français, donc tout est cohérent tant que vous restez dans cette version.
>
> | version anglaise | version française |
> |---|---|
> | `## Context` | `## Contexte` |
> | `## Acceptance criteria` | `## Critères d'acceptation` |
> | `## Out of scope` | `## Hors périmètre` |
> | `## Tasks` | `## Tâches` |
> | `## Definition of done` | `## Définition du terminé` |
> | `## As-built notes` | `## Notes de réalisation` |
> | `**Status:** 🔲 Backlog` | `**Statut :** 🔲 À faire` |
> | `**Status:** ✅ Done` | `**Statut :** ✅ Terminé` |
> | `As / I want / So that` | `En tant que / Je veux / Afin de` |
>
> **Ce qui ne change pas :** `US-NNN`, `epic-NNN-<nom>`, `WS-NN`, et tout chemin de fichier.

> **Questions à se poser avant d'écrire chaque section :**
>
> **En tant que / Je veux / Afin de**
> 1. Qui veut cela précisément — quel rôle nommé du glossaire, et non juste « un utilisateur » ?
> 2. Que veut-il pouvoir faire, en une phrase ?
> 3. Pourquoi ce résultat compte-t-il pour lui, et pas seulement pour vous qui construisez ?
>
> **Contexte**
> 1. Qu'est-ce qui existe déjà et sur quoi ceci s'appuie ?
> 2. Qu'est-ce qui ne doit explicitement PAS être supposé déjà fait ?
>
> **Critères d'acceptation**
> 1. Quel est le plus petit énoncé testable qui soit sans ambiguïté vrai ou faux une fois ceci terminé ?
> 2. Y a-t-il ici un critère qui est en réalité une tâche déguisée — une étape d'implémentation, et non un résultat observable ?
>
> **Hors périmètre**
> 1. Qu'est-ce qui est adjacent à cette user story et qu'un lecteur pourrait supposer inclus, sans l'être ?
>
> **Tâches**
> 1. Quelle est la prochaine action concrète, dans un ordre qu'on pourrait réellement suivre du début à la fin ?
>
> **Définition du terminé**
> 1. Que vérifie réellement, de ses propres yeux, la personne qui a demandé ceci pour l'accepter ?
>
> **Notes de réalisation**
> 1. Qu'est-ce qui a changé entre ce qui était prévu et ce qui a réellement été construit, et pourquoi ?
