---
name: check-project-docs
description: Audite les documents fondateurs du projet (PRD.md, NFR.md, SOLUTION_DESIGN.md, AGENTS.md, GLOSSARY.md) pour détecter l'obsolescence et la dérive par rapport à ce qui a réellement été construit, ainsi que la terminologie abandonnée qui revient. Ne fait que rapporter des constats — ne modifie jamais ces cinq fichiers sans confirmation explicite. À utiliser quand on demande de vérifier, auditer ou relire la cohérence des documents du projet, ou périodiquement après la clôture d'un Epic. Audits the foundational documents for staleness and drift.
created: 2026-09-08T17:38:40Z
updated: 2026-11-09T17:14:13Z
---

# Compétence : vérifier les documents du projet

## Pourquoi elle existe, et pourquoi ce n'est pas simplement « relire les documents pour voir si quelque chose cloche »

Les documents fondateurs (`PRD.md`, `SOLUTION_DESIGN.md`, etc.) dérivent parce qu'ils décrivent une *intention*, alors que `project-docs/execution/EPIC_EXECUTION.md` et `project-docs/technical-specs/` / `project-docs/functional-specs/` décrivent *ce qui a réellement été construit* — et seule la seconde catégorie est touchée à chaque livraison de user story. Une relecture vague ne fait généralement que reconfirmer ce qui est déjà cru. Cette compétence **compare au contraire les documents fondateurs à la vérité de terrain du réalisé**, plus une liste tenue à jour des termes que ce projet a explicitement abandonnés — c'est cela qui fait réellement apparaître la dérive, et non un contrôle de vraisemblance général.

**Rapport seulement. Ne modifiez jamais en silence `PRD.md`, `NFR.md`, `SOLUTION_DESIGN.md`, `AGENTS.md` ni `GLOSSARY.md`.** Tous les cinq sont des documents de granularité « par décision », « par décision d'architecture » ou « critique pour une session » (tableau de mise à jour des documents de `project-docs/PROJECT_WORKFLOW.md`) — toute divergence réelle trouvée dans l'un d'eux doit être remontée et confirmée avec le propriétaire du projet avant correction, jamais corrigée automatiquement.

## Liste de contrôle des termes abandonnés

Tenez et étendez cette liste à mesure que des termes sont abandonnés dans ce projet — ne la laissez pas devenir obsolète elle-même. **Un renommage ou une suppression ajoute une ligne ici dans le même commit qui l'effectue**, ou ce tableau devient précisément la chose obsolète qu'il existe pour attraper.

**Lisez la colonne « usages légitimes » avant de rapporter une occurrence.** La plupart de ces mots ont des sens honnêtes ailleurs, et un `grep` qui les signale est pire que pas de contrôle du tout : il entraîne le lecteur à sauter la sortie.

| Terme ou motif | Statut | Usages légitimes — pas un constat | Abandonné le |
|---|---|---|---|
| *(vide — ajoutez une ligne le jour où vous abandonnez votre premier terme)* | | | |

**Deux exemples travaillés de la forme, venant du projet dont cette compétence est issue — supprimez-les dès que vous avez de vraies lignes à vous :**

> | `level` (comme synonyme de l'unité d'enseignement du produit) | Abandonné — le mot est **`lesson`**. `AGENTS.md` § conventions | un niveau de **zoom**, un niveau de **titre ARIA**, un niveau d'**effort**. Les trois sont du vocabulaire courant | 2026-09-08 |
> | `✅ Accepté` comme état de user story | Abandonné — **il n'y a pas de cinquième état.** L'acceptation est ce qui rend une user story terminée ; écrivez `✅ Terminé — accepté le AAAA-MM-JJ` | le mot *accepté* à l'intérieur de cette chaîne, et la prose décrivant le propriétaire du projet qui accepte | 2026-09-10 |

Ce qui rend ces lignes utiles, c'est la **troisième colonne**, et c'est celle que les gens omettent. Les deux mots abandonnés ont des sens honnêtes ailleurs ; un `grep` qui signale chaque occurrence produit surtout des fausses alertes, et un contrôle dont la sortie est surtout du bruit est un contrôle que personne ne lit deux fois.

## Procédure

```
Avancement de la vérification :
- [ ] Étape 1 : lire les cinq documents fondateurs
- [ ] Étape 2 : lire la vérité de terrain (EPIC_EXECUTION.md + specs de Workstream)
- [ ] Étape 3 : chercher les termes abandonnés
- [ ] Étape 4 : recouper les références et la cohérence entre documents
- [ ] Étape 5 : chercher les décisions réelles non documentées
- [ ] Étape 6 : rapporter
```

**Étape 1 — Lire les cinq documents fondateurs** : `project-docs/PRD.md`, `project-docs/NFR.md`, `project-docs/SOLUTION_DESIGN.md`, **`AGENTS.md`**, `project-docs/GLOSSARY.md`.

> **`AGENTS.md`, pas `CLAUDE.md`.** Dans l'agencement de ce kit, `CLAUDE.md` est un fichier mince qui importe `AGENTS.md` et n'ajoute que des notes propres à Claude Code ; **`AGENTS.md` porte la carte des dossiers, les règles de dommage et les conventions**, et c'est le document chargé dans chaque session, ce qui fait d'une ligne obsolète chez lui la plus coûteuse de toutes. Lisez aussi `CLAUDE.md` — il devrait tenir en quelques paragraphes — mais auditez `AGENTS.md`. Une version antérieure de cette compétence nommait `CLAUDE.md` ici, et aurait manqué une carte des dossiers d'`AGENTS.md` contredisant la section des commandes du même fichier.

**Étape 2 — Lire la vérité de terrain** : `project-docs/execution/EPIC_EXECUTION.md` (ce qui est réellement terminé, par Epic) et chaque `project-docs/technical-specs/ws-tech-*.md` / `project-docs/functional-specs/ws-func-*.md` pour un Workstream dont une user story a été livrée. C'est à cela que l'étape 4 compare les documents fondateurs — et non à eux-mêmes.

**Étape 3 — Chercher les termes abandonnés.** Servez-vous de la liste ci-dessus, en chaînes exactes, à travers les cinq documents fondateurs (`Grep` sur le terme, limité à ces cinq fichiers). Chaque occurrence est un constat candidat — confirmez qu'il s'agit bien de l'usage abandonné (et non, par exemple, d'une note historique explicitement marquée comme dépassée) avant de le rapporter comme une dérive vivante.

**Étape 4 — Recouper les références et la cohérence entre documents :**
- Chaque chemin de fichier, numéro de section (`§N`) ou identifiant d'Epic / de Workstream cité dans les cinq documents fondateurs se résout-il encore ? (Un fichier de spec renommé, un `§` renuméroté après une édition, un numéro d'Epic retiré.)
- Le tableau des Workstreams de `SOLUTION_DESIGN.md` §2 correspond-il à la colonne Workstream de la vue d'ensemble des Epics de `PLAN.md`, et les définitions d'Epic / Workstream / Milestone de `GLOSSARY.md` correspondent-elles à la façon dont les deux sont réellement employés ?
- Quelque chose dans `PRD.md` ou `SOLUTION_DESIGN.md` décrit-il un composant, un flux ou un schéma que la vérité de terrain de l'étape 2 montre avoir été construit autrement ? (Par exemple une description du modèle d'accès dans `PRD.md` antérieure à une vraie décision de schéma consignée dans une spec technique.)
- **La carte des dossiers d'`AGENTS.md` §2** correspond-elle encore au dépôt — chaque chemin, et chaque fichier nommé à côté d'un chemin ? C'est le contrôle unitaire le plus rentable de cette compétence : la carte nomme des fichiers, les fichiers bougent, et rien n'échoue quand une ligne devient obsolète. Vérifiez que chaque chemin se résout avec `ls`, plutôt que de lire la carte et de la trouver plausible.
- **`AGENTS.md` se contredit-il ?** Il est assez long pour cela, et la carte de §2 nommant un chemin tandis que les commandes de §9 en nomment un autre est un défaut réel qui s'est déjà produit. Recoupez tout fichier mentionné dans plus d'une section.

**Étape 5 — Chercher les décisions réelles non documentées.** Cherchez les décisions qui se lisent comme de la granularité `PRD.md` (périmètre, produit) ou `SOLUTION_DESIGN.md` (architecture) mais n'ont jamais été réécrites dans l'un ou l'autre fichier — l'écart que la clôture d'`epic` attrape à une frontière d'Epic, attrapé ici entre deux. **La vérité de terrain est ce qui est committé**, donc lisez :

- `git log --oneline` depuis la dernière clôture d'Epic, en lisant le *corps* des commits — si votre projet y écrit son raisonnement, une décision consignée nulle part ailleurs y est généralement visible.
- Les fichiers les plus récents de `project-docs/reviews/`, là où une correction atterrit à l'instant où elle est trouvée.
- `PLAN.md` § Prochaines étapes immédiates, pour une décision décrite comme en attente et qui a depuis été prise.

Une décision qui n'existe que dans un corps de commit ou une revue, et qui est de granularité `PRD.md` ou `SOLUTION_DESIGN.md`, est le constat.

**Étape 6 — Rapporter.** Un constat par ligne : le fichier, ce qui est obsolète, contradictoire ou relève d'un terme abandonné, ce que dit réellement la vérité de terrain, et un correctif suggéré — mais n'appliquez aucun d'eux sans que le propriétaire du projet confirme lesquels traiter. Si rien n'est trouvé, dites-le franchement ; ne fabriquez pas de constats pour justifier la passe.
