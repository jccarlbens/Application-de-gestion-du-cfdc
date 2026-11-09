---
created: 2026-09-08T17:38:40Z
updated: 2026-11-09T17:14:13Z
---

# functional-specs/

**Répond à :** que fait réellement un Workstream livré, du point de vue du comportement ?

**Pas de gabarit figé.** Les sections se décident par Workstream, une fois qu'il y a un comportement réel à documenter — jamais à l'avance. Écrire une spécification fonctionnelle avant qu'une user story de ce Workstream se soit close, c'est de la spéculation, pas de la documentation.

**Convention de nommage des fichiers :** `ws-func-NN-nom.md`, où `NN` correspond exactement à l'identifiant du Workstream dans `SOLUTION_DESIGN.md` § Workstreams.

> **Questions à se poser pour décider si une section est nécessaire (et non pour remplir une liste figée) :**
> 1. Qu'est-ce qu'un utilisateur ou un système appelant observe maintenant, qu'il ne pouvait pas observer avant que ce Workstream existe ?
> 2. Quels sont les cas limites ou les conditions de refus qu'une personne construisant contre ceci doit connaître ?
> 3. Y a-t-il ici une règle qui n'est pas évidente à la lecture du code — une règle métier, une frontière de confidentialité, une exigence d'ordonnancement ?
>
> **La question qui gouverne tout le reste : une user story de ce Workstream s'est-elle réellement close ? Si non, il n'y a rien de réel à documenter — attendez.**
