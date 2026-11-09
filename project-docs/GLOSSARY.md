---
created: 2026-11-09T00:00:00Z
updated: 2026-11-09T17:14:13Z
---

# GLOSSARY.md — CFDC

**Répond à :** que veut dire ce terme ? — à consulter dès qu'un mot est ambigu, une fois rempli.
**Dépend de :** rien pour la section « Workstream, Epic et Milestone » (générique, déjà présente) ; de `PRD.md`, et surtout de `PLAN.md`, pour tout le reste.

> **Statut : structure de départ — le dernier document à finaliser, pas le premier.** Contre-intuitivement, ce n'est pas par là qu'on commence : sans savoir encore quel produit c'est, vous ne savez pas quel vocabulaire mérite une entrée. Le véritable ordre : `PRD.md` → `NFR.md` → `SOLUTION_DESIGN.md` → `PLAN.md` → **ici, en dernier**. Ce fichier peut commencer à se remplir dès qu'un premier brouillon de PRD existe (les premiers termes émergent), mais il ne se **finalise** qu'une fois `PLAN.md` terminé — c'est là qu'il y a assez de matière pour savoir vraiment quel produit c'est. Chaque section porte les questions de réflexion à se poser avant d'écrire — ne demandez pas à l'agent d'inventer les réponses.

---

## Acteurs et rôles

*(À écrire)*

> **Questions à se poser :**
> 1. Qui ou quoi touche ce système, et chacun a-t-il besoin de capacités, d'accès ou de niveaux de confiance différents ?
> 2. Y a-t-il un mot (comme « utilisateur » ou « agent ») qui pourrait désigner deux choses différentes selon le contexte, ici ? Faut-il le scinder en deux termes ?
> 3. Y a-t-il des modes ou des intentions distincts dans lesquels un même acteur peut se trouver, et qui méritent d'être nommés séparément ?

---

## Composants du système

*(À écrire)*

> **Questions à se poser :**
> 1. Quelles sont les pièces exécutables ou déployables indépendamment de ce système ?
> 2. Deux composants portent-ils des noms assez proches pour être confondus ? Qu'est-ce qui distingue chacun en une phrase ?
> 3. Y a-t-il un découpage naturel qui mérite d'être nommé comme catégorie (public contre privé, permanent contre à la demande) ?

---

## Magasins de données

*(À écrire)*

> **Questions à se poser :**
> 1. Où l'information persiste-t-elle réellement, et combien de magasins distincts y a-t-il ?
> 2. Un magasin détient-il plus d'une sorte de donnée qui mériterait d'être nommée séparément ?
> 3. Quel magasin, s'il était perdu, causerait le plus de dommages ?

---

## Vocabulaire du domaine

*(À écrire)*

> **Questions à se poser :**
> 1. Quels noms récurrents ou noms de processus une personne extérieure interpréterait-elle de travers sans définition ?
> 2. Quels termes reviennent sans arrêt dans les conversations sur ce projet sans être évidents à partir du mot seul ?
> 3. Y a-t-il un terme emprunté à un champ plus large qui signifie ici quelque chose de plus étroit ?

---

## Workstream, Epic et Milestone

*Générique — à réutiliser tel quel.*

- **Workstream** = *quel domaine fonctionnel*. Ne se termine jamais. Peut être revisité par un Epic ultérieur. Identifiant : `WS-NN` (deux chiffres).
- **Epic** = *quand, et quelle quantité à la fois*. Étape de construction séquentielle et bornée dans le temps. Identifiant : `epic-NNN-name` (dossier à trois chiffres).
- **Milestone** = *ce qui est livré*. La représentation GitHub d'un Epic — et non un quatrième concept distinct.

> **Question à se poser :** ce projet a-t-il véritablement besoin des trois axes, ou est-il assez petit pour que deux d'entre eux se confondent en un seul ? Quels sont les Workstreams réels de ce projet, indépendamment de l'ordre dans lequel ils seront construits ?

**Dans CFDC :** les Workstreams (`WS-NN`) seront définis dans `SOLUTION_DESIGN.md` §2, les Epics dans `PLAN.md`. *(À écrire une fois ces deux documents remplis.)*

---

## Documents du projet

*Générique — simple renvoi.*

Le document canonique listant tous les autres documents du projet : voir `PRD.md` § Documents liés.

---

*GLOSSARY.md — CFDC — structure de départ issue de `project-init-kit-fr/`.*
