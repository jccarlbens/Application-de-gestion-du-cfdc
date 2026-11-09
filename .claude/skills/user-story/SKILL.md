---
name: user-story
description: Créer, affiner, mettre à jour ou supprimer une user story de ce projet. La création écrit le fichier de spécification et la ligne de suivi. L'affinage est le cadrage avant construction d'une user story existante à faire — lire le code source, résoudre les questions ouvertes, consigner les décisions — avant qu'aucun code ne soit écrit. À utiliser dès qu'on demande d'écrire une nouvelle user story, de la cadrer avant de la construire, de changer le périmètre, le statut ou les tâches d'une user story existante, ou d'en supprimer une. Create, refine, update, or delete a user story.
created: 2026-09-08T17:38:40Z
updated: 2026-11-09T18:27:04Z
---

# Compétence : user story

> **Réglage, une fois, avant la première utilisation :** remplacez `[OWNER]/[REPO]` ci-dessous par vos véritables `owner/repo` GitHub, et `4` / `CFDC` par le numéro et le nom de votre tableau GitHub Projects (v2), si vous en utilisez un. Si vous n'utilisez pas du tout GitHub Issues ni Projects, adaptez le §3 et les procédures de création, de mise à jour et de suppression à l'outil de suivi que nomme `project-docs/PROJECT_WORKFLOW.md` § Suivi du travail. **`CLAUDE.md` porte cette décision** — lisez-la là plutôt que de la reprendre à chaque fois.

## 1. Vue d'ensemble

Autonome : cette compétence porte sa propre copie du format et des conventions ci-dessous, pour ne pas avoir à ouvrir `project-docs/PROJECT_WORKFLOW.md` pour s'exécuter. Ce fichier est la version lisible par un humain de la même matière — si les deux se contredisent un jour, prenez les vrais fichiers `US-*.md` de `project-docs/execution/` comme arbitre, puis corrigez celui des deux documents qui est obsolète.

Le vocabulaire employé ci-dessous (Workstream, Epic, Milestone) est défini dans `GLOSSARY.md` § Workstream, Epic et Milestone. Version courte : Workstream = domaine fonctionnel (non borné dans le temps). Epic = étape de construction cadrée et séquentielle, travaillée une à la fois — canonique dans `PLAN.md`. Milestone = point de contrôle livrable à l'intérieur d'un Epic, en pratique une release, représentée sur GitHub par un objet Milestone.

---

## 2. Format de user story

```markdown
# US-NNN : [Titre court]

**Statut :** 🔲 À faire / ✅ Terminé / etc.
**Milestone :** [titre exact du Milestone GitHub, par exemple « Epic 1 — <Nom> »]
**GitHub Issue :** [#N](https://github.com/jccarlbens/Application-de-gestion-du-cfdc/issues/N)
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

(Regroupez les critères sous des sous-titres `### ` pour une user story
comportant plusieurs domaines distincts.)

## Hors périmètre
- [Ce qu'il ne faut PAS construire dans cette user story]

## Tâches
- [ ] [Étape d'implémentation concrète]
- [ ] [...]

## Définition du terminé
- [ ] [Chose précise vérifiée dans le navigateur ou dans l'application]
- [ ] [Le propriétaire du projet] valide → la user story passe à Terminé

## Notes de réalisation
[Présentes seulement dès que le travail commence ou s'achève — ce qui s'est
réellement passé, les écarts par rapport au plan, les décisions prises en
chemin.]
```

**Identifiant de user story :** `US-001`, `US-002`, … séquentiel sur tout le projet — jamais réutilisé, jamais remis à zéro par Epic, jamais avec un trou.

**Tâches contre critères d'acceptation :** les critères = ce qui doit être vrai quand c'est terminé (résultats testables). Les tâches = les étapes pour y arriver (actions d'implémentation).

**Rôle :** toujours un nom issu de `GLOSSARY.md` § Acteurs et rôles. Le propriétaire du projet s'écrit « En tant que [propriétaire du projet] ».

**Corps de l'issue GitHub** (selon `project-docs/PROJECT_WORKFLOW.md`) contient UNIQUEMENT : l'énoncé « En tant que / Je veux / Afin de », un paragraphe de contexte, et une ligne `**Spec :** project-docs/execution/<dossier-epic>/US-NNN.md`. Jamais les critères d'acceptation, les tâches ni la définition du terminé — ceux-là ne vivent que dans le fichier de spécification.

> **Correspondance avec la version anglaise du kit.** Les intitulés de section sont traduits et les identifiants ne le sont pas. `## Context` → `## Contexte`, `## Acceptance criteria` → `## Critères d'acceptation`, `## Out of scope` → `## Hors périmètre`, `## Tasks` → `## Tâches`, `## Definition of done` → `## Définition du terminé`, `## As-built notes` → `## Notes de réalisation`, `🔲 Backlog` → `🔲 À faire`, `✅ Done` → `✅ Terminé`. Le tableau complet est dans `project-docs/templates/user-story.md`. **Restez dans une seule version** : mélanger les deux produit des fichiers que ni l'une ni l'autre ne sait lire.

## 3. Contexte GitHub Projects

Si un GitHub Project (v2, tableau) est utilisé : **« CFDC »**, numéro de projet `4`, propriétaire `jccarlbens` — `https://github.com/users/jccarlbens/projects/4`. Son champ à choix unique `Status` propose typiquement des options comme Backlog, To Do, In Progress, Review, Done. Chaque issue créée via la procédure de création de cette compétence (§ ci-dessous) doit être ajoutée à ce projet. Ne définissez ni ne changez jamais le champ `Status`, et ne déplacez jamais une issue d'un état du tableau à un autre — c'est le propriétaire du projet qui le fait manuellement. Cette compétence ne fait jamais que créer des issues, les ajouter au projet (en laissant `Status` à la valeur par défaut qu'applique le projet) et éditer le corps ou le titre ; elle ne touche pas à la position sur le tableau et ne ferme pas d'issue, sauf lors d'une suppression explicite (§ Suppression ci-dessous).

## 4. Définition du terminé

Une user story n'est terminée que lorsque : (1) tous les tests qu'elle spécifie passent ; (2) le propriétaire du projet effectue le contrôle précis listé dans la définition du terminé de la user story et ne trouve aucun problème ; (3) le propriétaire du projet donne une validation conjointe. Cette compétence ne marque jamais une user story comme terminée de sa propre initiative — seul le propriétaire du projet le fait, en conversation.

## 5. Référence de vocabulaire

Chaque terme employé dans une user story doit se résoudre en une définition de `GLOSSARY.md` (acteurs et rôles, composants du système, magasins de données, vocabulaire du domaine, Workstream / Epic / Milestone). Si un terme est ambigu ou absent, résolvez-le ou ajoutez-le à `GLOSSARY.md` avant d'écrire la user story.

---

## Procédure : créer une nouvelle user story

1. **Déterminer le prochain identifiant.** Parcourez `project-docs/execution/**/US-*.md`, prenez le plus grand `NNN`, utilisez `NNN+1`. Ne réutilisez et ne renumérotez jamais les user stories existantes.
2. **Déterminer le dossier d'Epic et le Milestone.** Consultez la vue d'ensemble des Epics de `PLAN.md` pour l'Epic actuellement actif (un seul l'est jamais — les Epics sont séquentiels, jamais parallèles, sauf si le `PLAN.md` de ce projet dit explicitement le contraire). Si la user story pourrait plausiblement servir plus d'un Epic, demandez au lieu de deviner. Confirmez le titre exact du Milestone auprès de GitHub : `gh api repos/jccarlbens/Application-de-gestion-du-cfdc/milestones --jq '.[] | {number, title}'`. Si aucun milestone correspondant n'existe encore, arrêtez-vous et demandez — n'en inventez pas. Notez quel ou quels Workstreams la user story touche principalement (d'après le tableau des Workstreams de `SOLUTION_DESIGN.md` §2) — mentionnez-le dans le contexte de la user story si ce n'est pas évident à partir du seul Epic.
3. **Écrire le fichier de spécification** à `project-docs/execution/<dossier-epic>/US-NNN.md` en suivant le format du §2. Le statut commence à `🔲 À faire`. Pas encore de section `Notes de réalisation`. Laissez la ligne GitHub Issue en espace réservé jusqu'à ce que l'étape 5 renvoie un vrai numéro.
4. **Rédiger le corps de l'issue** (titre : `US-NNN : [Titre court]` ; corps : énoncé de la user story + contexte + `**Spec :** project-docs/execution/<dossier-epic>/US-NNN.md`, selon la convention de corps d'issue du §2).
5. **Créer l'issue GitHub :**
   ```
   gh issue create --repo jccarlbens/Application-de-gestion-du-cfdc --title "US-NNN: [Titre court]" --body-file <fichier-temporaire> --milestone "<titre exact du milestone>"
   ```
   Récupérez l'URL et le numéro d'issue renvoyés.
6. **Ajouter l'issue au projet de suivi** (§3, s'il est utilisé) : `gh project item-add 4 --owner jccarlbens --url "<url-de-l-issue>"`. Ne définissez ni ne touchez le champ `Status` — le propriétaire du projet gère la position sur le tableau manuellement.
7. **Renseigner la ligne GitHub Issue** du fichier de spécification avec le vrai lien.
8. **Ajouter une ligne à `project-docs/execution/EPIC_EXECUTION.md`** dans le tableau de l'Epic correspondant, au statut `🔲 À faire`, avec un lien vers le nouveau fichier de spécification.
9. **Rapporter** le numéro de la nouvelle user story, le chemin du fichier de spécification et l'URL de l'issue, et confirmer que l'issue a été ajoutée au projet. Ne déplacez ni ne définissez pas le champ `Status` du projet pour le nouvel élément.

## Procédure : affiner une user story

Analyse avant construction d'une user story existante à faire — l'étape entre la création et l'implémentation effective. Analogue à la procédure d'affinage d'`epic`, un niveau plus bas. Ne touche jamais au statut, et ne marque jamais une user story comme prête ou terminée — seul le propriétaire du projet le fait (§4).

1. **Lire le code source, et pas seulement les documents.** La user story et tout ce qu'elle référence (spécifications fonctionnelles et techniques liées, documents de schéma, user stories nommées dans `Dépend de`) *ainsi que* le code réel que la user story va modifier. **Cette étape est placée en premier parce que la sauter a un coût mesuré.** Sur le projet dont cette procédure est issue, la section d'un Epic dans `PLAN.md` faisait trois affirmations sur le code ; la lecture d'un unique fichier source les a toutes les trois falsifiées. Un plan est écrit depuis la feuille de route ; une user story doit être écrite depuis le code source. **La user story la plus coûteuse est celle dont la prémisse était vraie au moment où la feuille de route a été écrite** — elle se lit comme correcte à chaque relecture, et seule la construction découvre le contraire.
2. **Trouver les véritables questions ouvertes** — exigences ambiguës, choix techniques non résolus, décisions auxquelles le contexte actuel ne répond pas déjà. Une question à laquelle le code source répond n'est pas une question ouverte ; résolvez-la en lisant.
3. **Chercher avant de demander**, quand la réponse dépend d'une bonne pratique externe plutôt que d'une préférence propre au projet (un choix de bibliothèque, une convention de protocole) — énoncez les constats et les sources avant de présenter des options.
4. **Demander au propriétaire du projet** avec des options concrètes et une recommandation quand il y en a une, et non des questions ouvertes.
5. **Consigner chaque décision** sous forme d'ajouts datés au `## Contexte` de la user story (`**Affiné le AAAA-MM-JJ, avant construction :**`), et mettre à jour `## Critères d'acceptation` et `## Tâches` dans la même passe, pour qu'ils *reflètent* les décisions au lieu de les raconter en prose à côté.
6. **Corriger une affirmation fausse sur place ; ne la supprimez pas discrètement.** Là où l'affinage réfute quelque chose que la user story ou `PLAN.md` affirmait déjà, écrivez la correction à côté de l'affirmation qu'elle remplace. Une section qui fait cela est généralement la moitié qui vaut encore d'être lue un an plus tard — une prémisse fausse effacée n'apprend à personne pourquoi la user story a changé de forme.
7. **Corriger tout renvoi obsolète** remarqué en lisant — un lien vers un fichier renommé, un numéro de section qui a bougé. Ne le laissez pas à `check-project-docs` à trouver plus tard.
8. **Rapporter** ce qui a été affiné et chaque décision prise.
9. **Proposer le plan d'implémentation** (`PROJECT_WORKFLOW.md` § Cycle de travail, étape « planifier ») : fichiers créés ou modifiés, migration, routes, écrans, tests, ordre des étapes. Le membre le relit et le corrige ; une fois validé, il remplace la section `## Tâches`. **N'écrivez aucun code avant cette validation explicite.**

**À quoi ressemble un bon affinage :** la user story qui en sort doit être constructible sans poser une question de plus, et son `## Contexte` doit consigner au moins une chose que la lecture du code source a *changée*. Un affinage qui confirme toutes les hypothèses dont il est parti signifie généralement que le code source n'a pas réellement été lu — l'étape 1 existe parce que c'est l'échec courant, pas un échec hypothétique.

## Procédure : mettre à jour une user story existante

1. **Localiser** le fichier de spécification : `project-docs/execution/**/US-NNN.md`.
2. **Appliquer le changement demandé** (tâches, critères d'acceptation, statut, notes de réalisation, etc.) directement dans le fichier de spécification.
3. **Si le statut a changé**, mettre à jour la ligne correspondante de `project-docs/execution/EPIC_EXECUTION.md` pour qu'elle concorde.
4. **Ne toucher à l'issue GitHub** que si l'énoncé de la user story, son titre ou son contexte lui-même a changé — les changements de critères d'acceptation, de tâches et de cases de la définition du terminé ne vont jamais sur GitHub (§2). Utilisez `gh issue edit <N> --title "…"` / `--body-file <fichier-temporaire>` selon le besoin.
5. **Ne marquez jamais la user story comme terminée et ne fermez jamais l'issue** dans le cadre d'une mise à jour — cela n'arrive que par validation explicite du propriétaire du projet (§4).
6. **Rapporter** exactement ce qui a changé et dans quels fichiers.

## Procédure : supprimer une user story

Destructif et touche à un état GitHub partagé — avant de faire quoi que ce soit, listez chaque fichier et chaque référence qui vont changer, et confirmez avec le propriétaire du projet.

1. **Chercher d'abord les renvois croisés :** `grep -rn "US-NNN" project-docs/ *.md` (et tout autre type de document employé). Une user story peut être référencée par le champ `**Dépend de :**` d'autres user stories, par `EPIC_EXECUTION.md`, par des apprentissages, ou par les documents de la racine. Listez chaque occurrence avant de toucher à quoi que ce soit.
2. **Supprimer le fichier de spécification** : `project-docs/execution/<dossier-epic>/US-NNN.md`.
3. **Supprimer la ligne** de `project-docs/execution/EPIC_EXECUTION.md`.
4. **Corriger chaque renvoi trouvé à l'étape 1** — par exemple le `**Dépend de :** US-NNN` d'une autre user story doit être mis à jour ou retiré, et non laissé pendant.
5. **Fermer (jamais supprimer) l'issue GitHub** avec un commentaire expliquant pourquoi : `gh issue close <N> --comment "…"`. Les issues sont un registre historique — en supprimer réellement une via `gh issue delete` est une action distincte et plus difficile à annuler, que cette compétence ne fait pas automatiquement ; si le propriétaire du projet veut explicitement que l'issue disparaisse plutôt qu'elle soit fermée, c'est une demande distincte et explicite à chaque fois.
6. **Rapporter** chaque fichier modifié et l'issue fermée, pour que rien n'ait été oublié.
