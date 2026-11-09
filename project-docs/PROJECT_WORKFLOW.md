---
created: 2026-11-09T00:00:00Z
updated: 2026-11-09T17:14:13Z
---

# PROJECT_WORKFLOW.md — CFDC

**Répond à :** comment le travail circule-t-il réellement, et quel document dois-je toucher et quand ?
**Dépend de :** tout ce qui précède — c'est le tissu conjonctif.

---

## Quel document mettre à jour, et quand

*Générique — réutilisez ce tableau tel quel, en n'ajustant les noms de documents que s'ils changent.*

| Document | Granularité | Mis à jour quand |
|---|---|---|
| `project-docs/execution/EPIC_EXECUTION.md` | Par user story | En continu — chaque fois que le statut d'une user story change |
| `project-docs/functional-specs/`, `project-docs/technical-specs/` | Par Workstream | De façon incrémentale, à mesure qu'une user story est livrée |
| `project-docs/reviews/` | **Par constat** | **À l'instant où une croyance se révèle fausse** — et non à la fin du travail. Voir le README de ce dossier ; c'est la ligne la plus souvent ignorée, et la seule dont le coût augmente avec l'attente |
| `project-docs/PLAN.md` | Par Epic | Seulement quand un Epic entier commence ou s'achève |
| `project-docs/PRD.md` | Par décision | Seulement quand une véritable décision de produit ou de périmètre change |
| `project-docs/SOLUTION_DESIGN.md` (§ ADR) | Par décision d'architecture | Quand un véritable choix d'architecture est fait ou change |
| `project-docs/NFR.md` | Par exigence | Quand une exigence de qualité, un risque ou une dépendance apparaît ou change |
| `project-docs/GLOSSARY.md` | Par terme | Avant qu'un terme nouveau ou ambigu ne soit employé ailleurs |
| `project-docs/learnings/` | Par pratique réutilisable | Quand une revue se révèle vraie au-delà de cette base de code. Écrit après coup, délibérément — contrairement à une revue |
| `project-docs/PROJECT_WORKFLOW.md` | Par convention | Quand une convention de processus change |
| `CLAUDE.md` / `AGENTS.md` | Faits critiques pour une session | Quand change un fait que chaque session doit connaître |
| `project-docs/execution/epic-NNN-*/epic-NNN-refinement.md` | Par Epic | Écrit à l'affinage, avant qu'aucune user story n'existe, mis à jour tant que l'Epic est ouvert. **Le seul endroit où une règle en cours de travail peut vivre** — vidé dans les documents ci-dessus à la clôture de l'Epic |
| `project-docs/exploration/` | Jamais mis à jour | Écrit une fois, gardé tel qu'il est arrivé, jamais rangé et jamais cité comme une décision |

> **Questions à se poser :**
> 1. Pour chaque document, quel événement du monde réel devrait déclencher sa mise à jour ?
> 2. Un document est-il mis à jour selon un calendrier au lieu de l'être quand le fait qu'il porte change réellement — signe qu'il n'est peut-être pas le bon propriétaire de ce fait ?
> 3. Quelle ligne, ici, ne s'est jamais déclenchée une seule fois ? Un `reviews/` intact après du travail réel ne veut pas dire que rien n'a été appris ; cela veut dire que les constats sont partis dans une conversation qui n'existe plus.
> 4. Prenez la dernière règle que vous avez appliquée. Quelle ligne ci-dessus en est propriétaire, et y est-elle réellement écrite — ou n'existe-t-elle que dans une revue, un message de commit, ou la tête d'un agent ? Une règle que l'équipe ne peut pas consulter est une règle qu'un seul d'entre vous suit.

---

## Suivi du travail (outil de suivi)

*À généraliser selon l'outil réellement employé — GitHub Issues/Projects, ou quelque chose de plus simple.*

> **Questions à se poser :**
> 1. Quel outil suivra réellement le travail — un tableau, un tableur, de simples issues ?
> 2. Par quels états le travail passe-t-il, et qui l'y fait passer ?
> 3. Des champs personnalisés sont-ils réellement nécessaires, ou la ligne `Status` du format de user story suffit-elle déjà ?

*(À écrire)*

> **Cette section est celle que les compétences `epic` et `user-story` consultent.** Ces deux-là sont écrites GitHub d'abord, pour le dépôt `jccarlbens/Application-de-gestion-du-cfdc` ; `CLAUDE.md` porte la décision et dit comment appliquer celle des deux voies que vous retenez. Répondez ici, puis élaguez `CLAUDE.md` en conséquence.

---

## Cycle de travail

> **Questions à se poser :**
> 1. Par quelles étapes passe un Epic, de sa création à sa clôture ?
> 2. Par quelles étapes passe une user story, et à quel moment le code a-t-il le droit de commencer ?
> 3. Qui travaille sur quoi en parallèle — une personne, une équipe ?

*Point de départ, repris de la méthode — à confirmer ou ajuster :*

**Pour chaque Epic, un à la fois** (`PLAN.md`)
1. **Créer l'Epic** (compétence `epic`) : son dossier, sa section dans `EPIC_EXECUTION.md`, son Milestone.
2. **Affiner l'Epic** : résoudre ses questions ouvertes et dresser la liste de ses user stories, dans `epic-NNN-refinement.md`.
3. **Pour chaque user story :**
   1. la **créer** (compétence `user-story`) : son fichier, son issue ;
   2. l'**affiner** : lire le code existant et trancher les dernières questions, avant d'écrire du code ;
   3. la **planifier** : l'agent propose un plan d'implémentation, relu et corrigé avant tout code. Le plan validé remplace la section `## Tâches` du fichier de la user story ;
   4. créer une **branche**, implémenter, ajouter les tests ;
   5. ouvrir une **pull request**, la faire relire, fusionner sur `main` ;
   6. vérifier la **définition du « terminé »** (ci-dessous), puis passer la user story à ✅ Terminé.

   Si une croyance se révèle fausse en route, elle s'écrit **tout de suite** dans `project-docs/reviews/`.
4. **Clôturer l'Epic** (compétence `epic`).

**Entre deux sessions avec l'agent**
1. `prepare-compact` : l'agent reporte le travail de la session dans les fichiers du projet et vérifie l'état de git.
2. Committer.
3. Lancer `/compact`, à la main : l'agent ne le fait jamais.
4. À la reprise : `get-work-status`.

---

## Format de user story

Voir `project-docs/templates/user-story.md` — copie du même format, ne le dupliquez pas ici.

---

## Définition du « terminé » (au niveau du projet)

> 1. Quel est le seuil universel que chaque user story doit franchir avant d'être terminée, indépendamment de sa propre définition du « terminé » ?

*(À écrire)*

---

## Référence de vocabulaire

Chaque terme employé dans les spécifications, dans ce document et dans les conversations doit se résoudre dans `GLOSSARY.md`.

> **Question :** chaque terme employé dans les spécifications est-il traçable jusqu'à une entrée du glossaire ?

---

## Étapes d'amorçage de l'outil de suivi

> **Question :** quelles sont les étapes de réglage, à faire une seule fois et dans l'ordre, dont a besoin quelqu'un qui démarre de zéro avant que la première user story puisse être créée ?

**Une étape est fixe, quel que soit l'outil de suivi retenu :**

```bash
git config core.hooksPath .githooks
```

Une commande, une fois par clone. Elle active `.githooks/pre-commit`, qui estampille `updated:` en UTC sur chaque fichier markdown indexé. Sautez-la et les dates cessent de bouger en silence, ce qui est pire que de ne pas en avoir — une date présente et fausse se lit comme vraie.

*(Le reste est à écrire une fois l'outil de suivi choisi.)*
