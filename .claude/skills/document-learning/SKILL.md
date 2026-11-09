---
name: document-learning
description: Écrire ou mettre à jour un fichier dans project-docs/learnings/ consignant une pratique transposable à un projet sans rapport avec celui-ci. Vérifie d'abord qu'il s'agit bien d'un apprentissage et non d'une revue ou d'un contenu produit, puisque deux autres dossiers ont une prétention plus forte sur la plupart des constats. À utiliser dès qu'un travail a produit une habitude réutilisable et peu évidente qui vaut d'être conservée au-delà de cette session. Write or update a learnings file.
created: 2026-09-08T17:38:40Z
updated: 2026-11-09T17:14:13Z
---

# Compétence : documenter un apprentissage

Automatise la convention de fichier d'apprentissage de `project-docs/PROJECT_WORKFLOW.md`, pour que la structure soit cohérente à chaque fois plutôt que reconstruite de mémoire d'après la précédente.

## Étape 0 — est-ce même un apprentissage ?

**Deux autres dossiers ont une prétention plus forte sur la plupart des constats, et c'est l'étape qui manquait.** `project-docs/learnings/README.md` est canonique ; posez les questions dans cet ordre et arrêtez-vous au premier oui :

| Question | Destination | Pas cette compétence |
|---|---|---|
| Est-ce du contenu qui *est* le produit — de la matière qu'un utilisateur ou un lecteur consomme ? | là où vit le contenu de votre produit | ✓ |
| Est-ce une correction de ce que nous croyions à propos de *ce* code ? | `project-docs/reviews/` | ✓ |
| Est-ce une pratique qui aiderait sur un projet sans rapport avec celui-ci ? | `project-docs/learnings/` | **cette compétence** |

**Dites laquelle c'est et pourquoi, avant d'écrire quoi que ce soit.** Un constat qui échoue à la troisième question n'est pas un petit apprentissage — il appartient ailleurs, et le classer ici fait de ce dossier un dépotoir dont personne ne croit plus les fichiers réutilisables. Le test honnête : *retirez chaque nom propre à ce projet. Reste-t-il quelque chose qui vaille d'être lu ?*

**Une revue est la source habituelle.** La plupart des apprentissages commencent comme une entrée de `reviews/` et sont extraits plus tard en demandant « est-ce que quelque chose là-dedans est vrai au-delà de cette base de code ? » — et **la revue reste où elle est.** Extraire ne la déplace ni ne la supprime ; la revue reste le meilleur document sur le code de ce projet-ci.

## La règle non négociable

**« Comment cela a été appris » doit inclure les véritables échecs et corrections, pas seulement le résultat final propre.** C'est la chose la plus importante que cette compétence impose. Un fichier d'apprentissage qui ne décrit que ce que la réponse finale s'est révélée être n'est pas ce à quoi sert cette convention — les mauvais virages, ce qui a été corrigé, et pourquoi, sont la véritable valeur réutilisable. Si un travail n'a comporté aucune correction réelle en chemin, cela mérite en soi une note d'une ligne plutôt que de gonfler la section avec un récit qui laisse croire à plus de drame qu'il n'y en a eu.

## Procédure

1. **Obtenir la vraie date et heure courantes** : depuis l'horloge réelle de votre shell (par exemple `Get-Date -Format "yyyy-MM-dd HH:mm:ss"` en PowerShell, ou `date "+%Y-%m-%d %H:%M:%S"`). Ne supposez jamais la date du jour d'après le contexte de la conversation — une session peut s'étaler sur un temps réel important, et une date supposée peut être fausse en silence.
2. **Vérifier s'il s'agit d'un sujet nouveau ou d'une mise à jour d'un sujet existant.** Parcourez `project-docs/learnings/` à la recherche d'un fichier couvrant déjà ce sujet. S'il en existe un, c'est une **mise à jour**, pas un nouveau fichier — allez à l'étape 3a. Sinon, c'est **nouveau** — allez à l'étape 3b.

3a. **Mise à jour d'un fichier existant :**
   - Portez `**Dernière mise à jour :**` à l'horodatage réel de l'étape 1 (laissez `**Premier apprentissage :**` intact).
   - Ajoutez le nouveau contenu dans les sections concernées — à la suite de « Points de vigilance », en ajoutant des lignes à « Erreurs courantes », en ajoutant une nouvelle entrée datée au « Journal des décisions » si le fichier en a un. Ne réécrivez pas les sections encore exactes.
   - Passez à l'étape 6.

3b. **Nouveau fichier — prenez le numéro suivant de la séquence.** `NN-nom-en-kebab-case.md` : `04-trusting-a-new-tool.md`, et non `trusting_a_new_tool.md`. Nommez-le d'après la **pratique**, et non d'après l'incident qui l'a produite.

   **Le numéro est l'ordre dans lequel le fichier a été écrit, attribué une fois et jamais réattribué.** Une insertion ultérieure prend le prochain numéro libre plutôt que celui que son sujet suggérerait — une citation dans un vieux message de commit doit continuer de pointer vers le même document. Trier par sujet un enregistrement de l'évolution d'une compréhension n'apprend rien.

4. **Écrire le bloc de métadonnées et le titre :**
```markdown
> **Premier apprentissage :** AAAA-MM-JJ HH:MM:SS
> **Dernière mise à jour :** AAAA-MM-JJ HH:MM:SS

# Titre — nommé d'après la pratique, pas d'après l'histoire qui l'a produite
```

5. **Écrire le corps, dans cet ordre :**
   - **`## Contexte`** — ce que ceci documente et, surtout, *pourquoi cela vaut d'être consigné comme connaissance réutilisable* — non pas seulement ce qui s'est passé, mais ce que des sessions ou des services futurs devraient autrement re-dériver.
   - **`## Comment cela a été appris`** — trois parties obligatoires :
     - **Le déclencheur** : ce qui a provoqué ceci (une demande directe, une critique, un bogue rencontré en vrai).
     - **Le chemin** : ce qui s'est réellement passé, avec assez de détail pour qu'un mauvais virage soit visible en tant que mauvais virage — et non lissé en « nous avons décidé X » quand la vraie séquence était « essayé Y, cassé à cause de Z, corrigé en X ».
     - **Les points de vigilance** : des pièges concrets — assez précis pour que quelqu'un dans la même situation le reconnaisse immédiatement, et non des conseils génériques.
   - **`## La règle`** — la recommandation réellement réutilisable, généralisée au-delà de l'instance unique qui l'a produite (employez des noms et des termes génériques là où l'original était propre à une user story ou à un service, afin que la règle se lise comme applicable ailleurs).
   - **`## Erreurs courantes`** — un tableau (`Erreur | Pourquoi c'est arrivé | Correctif`) de corrections *réelles*, qui ont eu lieu, et non hypothétiques. Laissez une note d'attente si le travail est encore en cours et que les erreurs ne se sont pas encore produites — ne préremplissez pas avec des erreurs imaginées.
   - **`## Journal des décisions — séquence des changements`** *(facultatif — à inclure pour un travail en plusieurs étapes comportant assez de décisions distinctes pour mériter une chronologie ; à sauter pour un apprentissage court à décision unique)* — entrées datées, en ajout seulement, dans l'ordre où les choses se sont réellement produites.

6. **Rapporter** le chemin du fichier (et, pour une mise à jour, ce qui a été ajouté par rapport à ce qui est resté inchangé).
7. **Demander si la structure elle-même doit changer aussi.** Un apprentissage qui dit *« la prochaine fois, montez un projet autrement »* a un second foyer : l'échafaudage qui monte les projets — ces compétences, `project-docs/_ARCHITECTURE_EXPLAINED.md`, les gabarits de documents. La prose et l'échafaudage sont censés être rafraîchis dans la même passe, et ils dérivent en silence quand ils ne le sont pas : un échafaudage qui pose encore la forme qu'un apprentissage vient de rejeter sera cru, parce qu'il *s'exécute*. Dites-le dans le rapport ; ne modifiez pas l'échafaudage en silence comme effet de bord de l'écriture d'un apprentissage.
