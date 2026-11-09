---
created: 2026-09-10T19:30:13Z
updated: 2026-11-09T17:14:13Z
---

# `learnings/` — les pratiques transposables à votre prochain projet

Un apprentissage est une **pratique transposable** : quelque chose qui vaut d'être fait sur n'importe quel projet, appris en le faisant sur celui-ci. Il est écrit pour quelqu'un qui ne lira jamais cette base de code — vous compris, dans dix-huit mois, en démarrant autre chose.

## Dans quel dossier cela va-t-il ?

Trois destinations, une question chacune. Posez-les dans l'ordre et arrêtez-vous au premier oui.

| Question | Destination |
|---|---|
| Est-ce du contenu que le produit lui-même enseigne ou livre ? | là où vit le contenu de votre produit — pas ici |
| Est-ce une correction de ce que vous croyiez à propos de *ce* code ? | **`../reviews/`** — daté, lié à un fichier, écrit à l'instant du constat |
| Est-ce une pratique qui aiderait sur un projet sans rapport avec celui-ci ? | **ici** |

**Posez la deuxième question honnêtement, car la plupart des constats appartiennent là.** Un apprentissage qui ne survit pas au retrait de tous les noms propres à ce projet est une revue classée dans le mauvais dossier. Le test : *retirez chaque nom propre à ce projet. Reste-t-il quelque chose qui vaille d'être lu ?*

**Une revue est la source d'où vient un apprentissage.** Plus tard, une relecture de `../reviews/` demande *est-ce que quelque chose là-dedans est vrai au-delà de cette base de code ?* — et quand la réponse est oui, cela devient un fichier ici tandis que **la revue reste exactement où elle est.** Extraire n'est pas déplacer.

## Nommage

`NN-<description-en-kebab-case>.md` : `04-trusting-a-new-tool.md`, et non `trusting_a_new_tool.md`. Le numéro enregistre **l'ordre dans lequel l'apprentissage est entré dans ce dossier**, attribué une fois et jamais réattribué — ce n'est ni un ordre de lecture ni une priorité, puisqu'on les consulte par sujet. Même convention que `reviews/`, pour la même raison. Les fichiers importés d'un autre projet sont renumérotés dans votre séquence plutôt que de garder celle de ce projet, qui ne dit rien de vrai ici.

## Structure

N'importe quelle forme qui serve le propos, mais ces quatre sections méritent leur place, et l'une est non négociable :

- **`## Contexte`** — ce que c'est, et pourquoi cela vaut d'être conservé plutôt que re-dérivé.
- **`## Comment cela a été appris`** — le déclencheur, puis **le chemin**, puis les pièges. **Le chemin doit montrer les mauvais virages en tant que mauvais virages.** « J'ai essayé Y, ça a cassé à cause de Z, corrigé en X » — et non lissé en « nous avons décidé X ». C'est là toute la valeur ; un fichier qui ne consigne que la réponse finale propre n'est pas un apprentissage, c'est de la documentation.
- **`## La règle`** — la recommandation réutilisable, généralisée au-delà de l'incident unique qui l'a produite.
- **`## Erreurs courantes`** — un tableau de corrections *réelles*, qui ont eu lieu. Jamais hypothétiques.

Si un travail n'a véritablement comporté aucun mauvais virage, écrivez-le en une ligne plutôt que de fabriquer un drame que le travail n'a pas eu.

---

