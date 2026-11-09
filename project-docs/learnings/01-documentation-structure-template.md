---
created: 2026-09-08T17:38:40Z
updated: 2026-11-09T17:14:13Z
---

> **Premier apprentissage :** 2026-08-11 18:23:37
> **Dernière mise à jour :** 2026-08-13 18:10:19

## Contexte

Ce fichier est la version extractible et réutilisable d'une taxonomie de documents apparue après deux sessions complètes de restructuration, d'audit et de nettoyage de renvois croisés sur un véritable produit multi-services. Il existe pour que démarrer un *nouveau* projet n'exige pas de re-dériver cette structure de zéro. Ce fichier est le « quoi », prêt à copier ; le projet dont il a été extrait a sa propre histoire, plus longue, du *pourquoi* chaque document a gagné son périmètre.

Une seconde annexe, [`02-document-section-reflection-questions.md`](02-document-section-reflection-questions.md), décompose chaque document du tableau ci-dessous en ses sections réelles et donne 3 à 5 questions de remue-méninges par section — employez-la quand vous démarrez effectivement un nouveau projet et remplissez ces documents, et non quand vous apprenez simplement la forme d'ensemble.

## Comment cela a été appris

**Le déclencheur :** après une passe d'audit fichier par fichier complète sur un projet vivant, le propriétaire a demandé de « consigner la carte finale » pour que la même structure puisse être rebâtie pour un projet futur « à peu près » depuis ce modèle plutôt que de mémoire.

**Le déclencheur de l'addendum :** une demande a suivi, de couvrir aussi la couche *en dessous* de `CLAUDE.md` que la passe initiale n'avait pas touchée : la distinction entre `CLAUDE.md` et le standard ouvert `AGENTS.md`, le fonctionnement des `CLAUDE.md` imbriqués par dossier, et une représentation complète de ce qui peut vivre dans `.claude/` (règles, compétences, commandes, agents, workflows, hooks, MCP, plugins, worktrees) — parce que le plan était de réutiliser exactement cette structure de documents pour un second projet, plus petit, et que la couche d'extension avait besoin d'être documentée d'avance plutôt que redécouverte. Recherché contre la documentation officielle de Claude Code de l'époque plutôt que supposé, puisque cette couche change fréquemment d'une version à l'autre. Une demande ultérieure dans la même session a tiré l'arborescence physique réelle du projet directement dans ce fichier, pour que les règles de nommage qui s'y trouvaient déjà en prose côtoient un véritable exemple travaillé au lieu de rester abstraites — puis a demandé que cette arborescence soit anonymisée : nom du projet généricisé en `<project-root>/`, noms d'Epic et de user story réduits à leur motif `epic-NNN-<nom>` / `US-NNN`, et chaque dossier propre à *ce que* ce projet-là construit (dossiers de service, sa couche de données) retiré, de sorte que ce qui reste est la forme minimale et véritablement générique de la couche documentaire, et non l'instantané d'un produit.

**Le chemin :** la structure ci-dessous n'est pas celle avec laquelle le projet d'origine a démarré. Elle a traversé un vrai renommage de Phase en Epic, deux réorganisations de dossiers, une scission du PRD et du NFR, un démêlage entre Workstream et Epic, une restructuration du suivi d'exécution (un `EPIC_EXECUTION.md` à plat, des `functional-specs/` et `technical-specs/` séparés, des dossiers d'Epic et de Workstream à numérotation complétée par des zéros), et un audit final de cohérence fichier par fichier qui a attrapé de vraies dérives : tableaux dupliqués, renvois à des numéros de section obsolètes, vocabulaire de statut incohérent, étiquettes de persona discordantes, et un document (`GLOSSARY.md`) qui affirmait que son propre tableau était canonique ailleurs tout en en contenant encore une copie intégrale deux lignes plus bas.

**Points de vigilance :** chacun de ces documents a gagné son périmètre à la dure, en ayant d'abord le mauvais périmètre et en étant pris en flagrant délit de chevauchement avec un autre. Copier la *forme* ci-dessous dans un nouveau projet le premier jour est très bien. Copier du contenu dans le mauvais document, ou sauter le contrôle « est-ce que cela ne dit pas déjà cela » avant d'écrire, reproduira exactement la dérive pour laquelle ce nettoyage a été nécessaire en premier lieu.

## La règle

### L'ensemble de documents, dans l'ordre des dépendances

| # | Document | Répond à | Dépend de |
|---|---|---|---|
| 1 | `GLOSSARY.md` | Que veut dire ce terme ? | Rien — à lire en premier quand un terme est ambigu |
| 2 | `PRD.md` | Que construisons-nous, pour qui, pourquoi ? | Le glossaire, pour le vocabulaire |
| 3 | `NFR.md` | Quel niveau de qualité doit-il atteindre ? | Le PRD (compagnon, et non un sous-ensemble) |
| 4 | `SOLUTION_DESIGN.md` | Comment est-ce construit ? En quels Workstreams cela se décompose-t-il ? | PRD + NFR |
| 5 | `PLAN.md` | Dans quel ordre, regroupé en quels Epics ? | `SOLUTION_DESIGN` pour les identifiants de Workstream |
| 6 | `project-docs/execution/EPIC_EXECUTION.md` | Quel est le statut de chaque user story, à l'instant ? | `PLAN` pour les noms d'Epic |
| 7 | `project-docs/functional-specs/`, `project-docs/technical-specs/` | Que fait réellement un Workstream livré / comment est-il réellement construit ? | Écrits de façon incrémentale à mesure que les user stories se closent, jamais d'avance |
| 8 | `project-docs/execution/epic-NNN-*/US-NNN.md` | Qu'a-t-on précisément demandé et accepté pour une unité de travail ? | Rien — l'unité atomique que tout le reste résume |
| 9 | `project-docs/PROJECT_WORKFLOW.md` | Comment le travail circule-t-il réellement dans le système, et quel document dois-je toucher et quand ? | Tout ce qui précède, c'est le tissu conjonctif |
| 10 | `.claude/skills/<nom>/SKILL.md` | La version exécutable du n° 9, pour une tâche récurrente | `PROJECT_WORKFLOW` (copie autonome, ne le relit pas à l'exécution) |
| 11 | `CLAUDE.md` | De quoi chaque session a-t-elle besoin avant de toucher à quoi que ce soit ? | Tout ce qui précède — c'est le résumé *dérivé*, construit en dernier, pas en premier |

Chaque ligne répond à exactement une question. Si un morceau de contenu pouvait répondre aux questions de deux lignes, il appartient à celle qui est la plus spécifique, et chaque autre ligne reçoit un renvoi au lieu d'une copie.

**Délibérément absent de ce tableau : un document de stratégie de test.** Quel ou quels cadres de test employer et comment les tests fonctionneront réellement ne se décide pas d'avance dans ce modèle — cette décision est laissée à émerger quand il y a du code réel à tester, plutôt que spéculée avant qu'une première ligne de code n'existe. Si un projet atteint le point où il a réellement besoin de le décider, cela atterrirait le plus naturellement comme une nouvelle ligne de ce tableau, ou se fondrait dans la section Maintenabilité existante de `NFR.md` (qui demande déjà s'il existe une suite de tests et ce qu'elle couvre) — et non inventé avant qu'il y ait une première ligne de code pour laquelle écrire des tests.

### Conventions de nommage non négociables

- **Workstream** (domaine fonctionnel, non borné dans le temps) : `WS-NN`, deux chiffres complétés par des zéros (`WS-00`… `WS-06`). Deux chiffres parce qu'un projet ne dépassera pas réalistement 99 domaines fonctionnels — les Epics et les user stories sont un compte différent, à croissance plus rapide, et reçoivent leur propre complétion.
- **Epic** (étape de construction séquentielle et bornée dans le temps, une active à la fois) : `epic-NNN-nom`, dossiers à trois chiffres complétés par des zéros (`epic-000-…`, `epic-001-…`).
- **User story** : `US-NNN`, séquentiel sur *tout le projet*, jamais remis à zéro par Epic, jamais réutilisé.
- **Fichiers de spécification fonctionnelle et technique** : `ws-func-NN-nom.md` / `ws-tech-NN-nom.md`, correspondant exactement à l'identifiant à deux chiffres du Workstream.
- **Dossiers de service** (dès qu'un projet se scinde en plusieurs services backend ou frontend) : `<acteur>-<service>` (par exemple `user-backend` / `admin-backend`, ou quelle que soit la scission d'acteurs), toujours avec des tirets, à plat à la racine du dépôt, jamais concaténés, jamais imbriqués sous un dossier parent commun.

### L'arborescence physique, modèle générique

Copiez cette forme telle quelle dans un nouveau projet ; seul le contenu de chaque fichier change :

```
<project-root>/
├── README.md                     <- comment un inconnu le lance
├── AGENTS.md                     <- ligne 11 : résumé dérivé, construit en dernier, reste mince
├── CLAUDE.md                     <- un simple import d'AGENTS.md, plus les notes propres à Claude Code
├── .claude/
│   ├── settings.json             <- committé : configuration des permissions et des hooks
│   ├── settings.local.json       <- ignoré par git : surcharges personnelles
│   └── skills/
│       └── <nom-compétence>/SKILL.md <- ligne 10 : version exécutable de PROJECT_WORKFLOW.md, une tâche récurrente
├── .githooks/pre-commit          <- estampille `updated:` sur le markdown indexé
│
├── project-docs/                 <- TOUS les documents sur la construction du projet
│   ├── PRD.md                    <- ligne 2 : quoi, pour qui, pourquoi
│   ├── NFR.md                    <- ligne 3 : le niveau de qualité, compagnon du PRD et non un sous-ensemble
│   ├── SOLUTION_DESIGN.md        <- ligne 4 : architecture, Workstreams (WS-NN), ADR
│   ├── PLAN.md                   <- ligne 5 : séquencement des Epics, lié aux identifiants de Workstream
│   ├── GLOSSARY.md               <- ligne 1 : vocabulaire, à lire en premier quand un terme est ambigu
│   ├── PROJECT_WORKFLOW.md       <- ligne 9 : quel document toucher, et quand
│   ├── _ARCHITECTURE_EXPLAINED.md         <- comment le code est découpé, et pourquoi
│   ├── execution/
│   │   ├── EPIC_EXECUTION.md              <- ligne 6 : statut continu, par user story
│   │   ├── epic-000-<nom>/                <- dossier d'Epic à trois chiffres complétés par des zéros
│   │   └── epic-001-<nom>/US-NNN.md       <- ligne 8 : séquentiel sur tout le projet, jamais remis à zéro par Epic
│   ├── functional-specs/ws-func-NN-*.md   <- ligne 7 : deux chiffres, correspond exactement au WS-NN du Workstream
│   ├── technical-specs/ws-tech-NN-*.md    <- ligne 7 : même appariement, côté implémentation
│   ├── reviews/NN-<nom>.md       <- ce qui était cru ici et s'est révélé faux
│   ├── learnings/NN-<nom>.md     <- ce fichier vit ici
│   ├── templates/user-story.md   <- copié une fois par user story
│   └── exploration/              <- recherche brute, gardée telle quelle, jamais citée comme décidée
│
└── <le code source du produit>   <- frontend/, backend/, quelle que soit la chose réellement construite
```

**Une seule règle gouverne cette organisation : `project-docs/` contient tous les documents qui parlent de *construire* le projet, et rien qui *soit* le produit.** La racine ne garde que ce qu'une première session doit lire sans qu'on le lui dise.

**Et pas de point en tête.** Un dossier commençant par un point est un contrat avec l'outillage signifiant *propriété d'une machine* : `ls` l'omet, l'Explorateur le cache, et la plupart des outils de recherche le sautent sans option — donc les documents derrière un tel dossier sont invisibles pour tout contrôle d'obsolescence qui fonctionne par `grep`. `.claude/` porte un point parce que rien ne le cherche et que chaque agent reçoit ce chemin littéralement. Ces documents-ci sont pour un humain.

L'endroit où vivent le code source et les dossiers de service du projet (frontend, backend, une couche de données, quelle que soit la nature du produit) est hors du périmètre de ce modèle, à dessein — c'est propre au produit, et non une partie de la forme documentaire réutilisable. Ce fichier normalise la couche documentaire qui se trouve au-dessus du code ; **`project-docs/_ARCHITECTURE_EXPLAINED.md` en est le pendant pour le code lui-même**, et la carte des dossiers de l'`AGENTS.md` du projet consigne la disposition réelle et concrète.

### Les trois axes de suivi de construction, gardés délibérément séparés

- **Workstream** = *quel domaine*. Ne s'achève pas. Peut être revisité par un Epic ultérieur.
- **Epic** = *quand, et quelle quantité à la fois*. Qu'un projet enchaîne les Epics de façon séquentielle (l'un terminé avant que le suivant ne commence) ou autorise un peu de parallélisme est une contrainte propre au projet — énoncez-la explicitement, ce n'est pas une propriété universelle d'« Epic ».
- **Milestone** = *ce qui est livré*. La représentation native GitHub d'un Epic, et non un quatrième concept.

### Quel document mettre à jour, et quand (la partie qui empêche la dérive)

Le tableau complet vit dans `project-docs/PROJECT_WORKFLOW.md` § Quel document mettre à jour, et quand — copiez ce tableau mot pour mot dans le `PROJECT_WORKFLOW.md` d'un nouveau projet, puis ajustez seulement les noms de documents. La version en une ligne : **le détail des user stories est continu, le détail des Epics est par Epic, les décisions produit sont par décision, les décisions d'architecture reçoivent une entrée d'ADR sur place, et tout le reste ne se met à jour que lorsque le fait qu'il énonce change réellement.** Ne mettez jamais à jour selon un calendrier, et jamais de façon spéculative.

### Les registres de décision d'architecture vivent à l'intérieur du document de conception

Pas un fichier à part, pas un dossier à part. Un seul tableau, à la fin de `SOLUTION_DESIGN.md`, dont les entrées ne sont jamais supprimées, seulement marquées `Dépréciée` avec une date et une raison. Cela garde « l'architecture actuelle » et « pourquoi ce n'est pas l'autre chose » dans le même document, c'est-à-dire là où quelqu'un a réellement besoin des deux en même temps.

### `CLAUDE.md` se construit en dernier, et reste mince

Chacun des autres documents ci-dessus est une source ; `CLAUDE.md` est le résumé dérivé, toujours chargé. Concrètement : une carte des dossiers, un renvoi vers la pile technique (et non un tableau de pile technique recopié), les contraintes de confidentialité et de comportement propres à ce projet, un ordre de lecture pour une première session (chemin de reprise rapide + chemin d'orientation complète), et une section de renvois nommant quel document est canonique pour quoi, sans jamais intégrer le contenu de ce document. Visez moins de ~300 lignes. Pour chaque ligne, le test est : est-ce que supprimer ceci provoquerait une action erronée ? Si non, coupez ou transformez en renvoi.

### `CLAUDE.md` contre `AGENTS.md`

`AGENTS.md` est un standard ouvert et indépendant des outils (sous l'égide de la Linux Foundation, des dizaines de milliers de dépôts fin 2025) : du markdown simple, aucun champ obligatoire, lu nativement par Codex, Cursor, Copilot, Gemini CLI, Aider, Windsurf et plus de vingt autres outils. **Claude Code ne lit pas `AGENTS.md` nativement.** Si un dépôt a besoin des deux (plusieurs outils d'IA en jeu), le motif pris en charge est un `CLAUDE.md` mince qui l'importe et ajoute les instructions propres à Claude en dessous :

```markdown
@AGENTS.md

## Claude Code
Utilise le mode plan pour les changements sous src/billing/.
```

Un lien symbolique (`ln -s AGENTS.md CLAUDE.md`) fonctionne aussi s'il n'y a rien de propre à Claude à ajouter, mais il exige des droits d'administration sous Windows ; l'import par `@` est donc le choix par défaut le plus portable.

**Quand employer lequel :** un projet à un seul outil (seul Claude Code touche le dépôt) n'a besoin que de `CLAUDE.md` — ajouter `AGENTS.md` par-dessus est une pure duplication que rien ne lit d'une seconde façon. `AGENTS.md` gagne sa place dès l'instant où un second outil de codage par IA rejoint le projet ; à ce moment-là il devient la source de vérité partagée et `CLAUDE.md` se réduit à un import plus un bref addendum propre à Claude.

### `CLAUDE.md` imbriqués et `.claude/rules/`

Deux mécanismes différents pour cadrer des instructions en dessous de la racine du projet, tous deux réels et tous deux à connaître avant de se rabattre sur « tout va dans le `CLAUDE.md` de la racine » :

- **`CLAUDE.md` imbriqué** (ou `CLAUDE.local.md`) : un `CLAUDE.md` à l'intérieur d'un sous-répertoire du répertoire de travail est découvert automatiquement mais se charge **à la demande**, seulement quand Claude lit effectivement un fichier de ce sous-arbre — et non au lancement de la session. Les `CLAUDE.md` ancêtres (du répertoire courant en remontant jusqu'à la racine du système de fichiers) se chargent au contraire intégralement au lancement, ordonnés racine d'abord pour que le fichier le plus spécifique soit lu en dernier. Employez cela pour un sous-arbre au contexte véritablement différent — un dossier de service avec son détail propre à Python, sans pertinence pendant qu'on travaille sur un frontend sans rapport, par exemple.
- **`.claude/rules/*.md`** : le mécanisme frère, cadré par motif de fichiers plutôt que par répertoire. Une règle avec un frontmatter `paths:` (par exemple `src/api/**/*.ts`) ne se charge que quand Claude lit un fichier correspondant ; une règle sans `paths:` se charge au lancement, à la même priorité que `.claude/CLAUDE.md`. Choisissez cela quand la séparation se fait par *type de fichier ou par convention* en travers de tout l'arbre (par exemple « conventions de test », « règles de conception d'API ») plutôt que par *répertoire*.

Recommandation officielle : scindez le `CLAUDE.md` de la racine dès qu'il approche les ~200 lignes — les fichiers longs se chargent toujours intégralement, mais réduisent le respect des instructions.

### Le dossier `.claude/`

Tout ce que Claude Code lit et qui est propre à un projet :

```
.claude/
├── settings.json         committé    — permissions, hooks, modèle, environnement, statusLine
├── settings.local.json   ignoré      — surcharges personnelles, même schéma que ci-dessus
├── CLAUDE.md             committé    — alternative au CLAUDE.md de la racine, même effet
├── rules/*.md            committé    — instructions cadrées par sujet, `paths:` facultatif
├── skills/<nom>/SKILL.md committé    — procédures exécutables pour les tâches récurrentes
├── commands/<nom>.md     committé    — ancienne /commande en un seul fichier ; les compétences la remplacent
├── agents/<nom>.md       committé    — « sous-agents » : contexte isolé, accès propre aux outils
├── workflows/<nom>.js    committé    — scripts d'orchestration de plusieurs sous-agents
├── output-styles/        committé    — seulement si l'équipe partage un style personnalisé
└── agent-memory/<agent>/ écrit par Claude — seulement pour les sous-agents dotés de mémoire
```

Plus deux choses qui vivent à la racine du projet et non dans `.claude/` : `.mcp.json` (committé, serveurs MCP partagés par l'équipe auxquels Claude Code se connecte lui-même) et `CLAUDE.local.md` (ignoré par git, notes personnelles de projet, frère d'un `settings.local.json` ignoré).

**Collision de nommage qui vaut d'être signalée dans tout projet définissant son propre vocabulaire métier autour du mot « agent »** : `.claude/agents/` est un mécanisme distinct de la plateforme Claude Code (les « sous-agents » — un assistant à fenêtre de contexte isolée auquel Claude délègue, par exemple un sous-agent relecteur de code). Si le produit d'un projet a déjà un concept d'« agent » (un agent d'IA visible par l'utilisateur, disons), dites-le explicitement en conversation et dans le fichier lui-même, puisque « l'agent » serait sinon un terme surchargé.

### Points d'extension avancés, documentés mais pas toujours adoptés

Quatre pièces de plus de l'écosystème `.claude/`, réelles et actuelles, dont tout projet n'a pas nécessairement besoin. Documenter la décision d'en sauter une, quand c'est le choix, en fait une décision plutôt qu'une lacune :

| Mécanisme | Ce que c'est | Où cela vit | À adopter quand… |
|---|---|---|---|
| **Hooks** | Des commandes shell déterministes que Claude Code exécute à des événements du cycle de vie (`PreToolUse` peut bloquer net un appel d'outil, `PostToolUse` s'exécute après qu'un appel a réussi, `SessionStart` se déclenche au lancement, à la reprise ou à la compaction). Contrairement à `CLAUDE.md`, ceux-ci sont appliqués quoi que Claude décide — les règles de réglages sont appliquées par le client, pas par le jugement de Claude. | La clé `hooks` dans `settings.json` (portée projet, utilisateur ou locale) — et non un dossier à part | Une règle de `CLAUDE.md` est sans cesse décrite mais pas suivie de façon fiable (par exemple « lance toujours le linter avant de committer ») — c'est le signal qu'il faut la promouvoir d'instruction indicative à hook `PreToolUse` ou `PostToolUse` appliqué, au lieu d'écrire la phrase une troisième fois |
| **MCP (`.mcp.json`)** | La configuration *propre* à Claude Code pour se connecter lui-même, en tant qu'outil de codage, à des serveurs MCP externes (GitHub, une base de données, un outil de design) pendant une session. **Collision de nommage à signaler explicitement** : c'est sans rapport avec l'architecture de serveur MCP qu'un projet prévoirait pour son propre produit, s'il en a une — ceux-là seraient des services que le projet construit dans le cadre de son produit, et non quelque chose que Claude Code, le CLI, lit pour s'étendre lui-même | `.mcp.json` à la racine du projet, committé, partagé par l'équipe | L'équipe veut que Claude Code lui-même (et non le produit) lise depuis un système externe en cours de session — par exemple interroger un gestionnaire de tickets vivant au lieu de coller le texte d'un ticket dans la conversation |
| **Plugins** | Un paquet autonome et distribuable de compétences + agents + hooks + serveurs MCP (+ serveurs LSP), soit installé depuis une place de marché, soit découvert automatiquement sans aucune étape d'installation via un manifeste `.claude-plugin/plugin.json` | Un répertoire de plugin, installé à la portée utilisateur ou projet | **La réponse directe à la réutilisation de la structure d'un projet dans un projet frère sans dérive par copier-coller** : dès qu'une compétence ou un jeu de règles est destiné à être partagé et à rester en phase entre dépôts plutôt que dupliqué à la main, empaquetez-le en un plugin et activez-le dans les deux, au lieu de maintenir deux copies indépendantes |
| **Worktrees** | Des copies git parallèles isolées (option `--worktree` / `-w`, `.claude/worktrees/<nom>/`, `.worktreeinclude` pour copier dans chacune les fichiers ignorés comme `.env`, `isolation: worktree` pour un sous-agent), pour que plusieurs sessions modifient sans se heurter | `.claude/worktrees/` (à ajouter au `.gitignore`), `.worktreeinclude` à la racine du projet | Utile dès l'instant où le modèle de travail d'un projet autorise plusieurs sessions en parallèle. **Non applicable** si le modèle de travail énoncé d'un projet est explicitement séquentiel — un agent, une user story à la fois, aucun travail parallèle — les worktrees existent précisément pour faire tourner des sessions isolées en parallèle, l'inverse de cette contrainte |

### Ordre de lecture pour une session fraîche

**Reprise rapide :** `project-docs/execution/EPIC_EXECUTION.md`, puis `PLAN.md` § Prochaines étapes immédiates, puis — si un Epic est ouvert — l'`epic-NNN-refinement.md` de cet Epic, que nomme `EPIC_EXECUTION.md`.

**La passation, ce sont les fichiers committés, et non une note de passation séparée.** Une version antérieure de ce modèle envoyait une session qui reprend vers des fichiers de brouillon ignorés par git. Les documents suivis battent les notes de brouillon pour la raison même qui fait exister le contrôle de version : ils sont relus, ils sont partagés, et ils ne peuvent pas être discrètement la copie obsolète.

**Orientation complète :** `PRD.md` → `NFR.md` → `SOLUTION_DESIGN.md` → `PLAN.md` → `project-docs/execution/EPIC_EXECUTION.md` → `project-docs/functional-specs/` + `project-docs/technical-specs/` → `project-docs/PROJECT_WORKFLOW.md` + la compétence concernée. `GLOSSARY.md` est une référence permanente en dehors de cette séquence, consultée à la demande.

## Tableau des erreurs courantes

| Erreur | Pourquoi cela arrive | Le correctif |
|---|---|---|
| Recopier un tableau dans un second document « pour la commodité » | Cela paraît utile sur le moment | Un seul emplacement canonique par fait, toujours. Toute autre mention est un renvoi, même si cela coûte un clic de plus |
| Renuméroter une section et s'arrêter quand les titres ont l'air corrects | Le correctif évident (les titres) est visible ; les renvois ne le sont pas | Après toute renumérotation, cherchez dans *tout le dépôt* les motifs `Section N` / `§N`, pas seulement dans le fichier que vous avez modifié, et pas seulement dans les fichiers qui ressemblent à des « candidats évidents » |
| Inventer une nouvelle convention de mise en forme au lieu de trouver celle déjà employée | Plus rapide que de chercher | Cherchez comment la même sorte de chose est déjà écrite ailleurs avant de mettre en forme quelque chose de nouveau |
| Traiter une question réflexive « qu'en penses-tu » comme une instruction à exécuter | L'empressement à être utile | Si le message est formulé comme une question, répondez d'abord à la question. Attendez un feu vert explicite avant d'écrire quoi que ce soit |
| Ajouter une dimension de statut ou d'avancement à un document censé être intemporel (un glossaire, par exemple) | Le statut paraît être un contexte utile | Une définition répond à « qu'est-ce que c'est », pas à « est-ce déjà construit ». Gardez un champ `Statut` séparé et explicite si c'est véritablement nécessaire, et n'enterrez jamais le statut de livraison dans la prose de la définition |
| Laisser le texte d'un document non mis à jour après avoir déplacé ce qu'il décrit | Le déplacement lui-même donne l'impression d'être toute la tâche | Si un document dit « la version canonique de X est ici », et que X déménage, cette phrase doit déménager ou être réécrite aussi : elle fait partie du contenu, elle n'est pas accessoire |
| Supposer qu'un outil agentique lit `AGENTS.md` automatiquement parce qu'il existe dans le dépôt | Les deux fichiers se ressemblent et tous deux décrivent des « instructions pour agents d'IA » | Claude Code ne lit que `CLAUDE.md`. Un `AGENTS.md` que rien n'importe via `@AGENTS.md` est invisible pour Claude Code, aussi complet soit-il |
| Reconstruire à la main le même jeu réutilisable de compétences, de hooks ou de règles une seconde fois dans un projet frère au lieu de l'empaqueter une fois | Copier-coller un dossier est plus rapide sur le moment que de mettre en place un plugin | Dès qu'un morceau de `.claude/` est destiné à être partagé entre dépôts, empaquetez-le en plugin pour que les deux projets lisent une seule source au lieu de s'éloigner en silence |

### Sources

Recherché contre la documentation officielle de Claude Code (toute sous `code.claude.com`, vers lequel `docs.anthropic.com/en/docs/claude-code/*` redirige désormais) :

- [How Claude remembers your project](https://code.claude.com/docs/en/memory) — hiérarchie et ordre de chargement de `CLAUDE.md`, interopérabilité avec `AGENTS.md`, `.claude/rules/`
- [Explore the `.claude` directory](https://code.claude.com/docs/en/claude-directory) — référence complète des fichiers et dossiers de `.claude/` aux portées projet et utilisateur
- [Plugins reference](https://code.claude.com/docs/en/plugins-reference) — composants d'un plugin, portées d'installation, plugins de type répertoire de compétences (manifeste seul)
- [Automate actions with hooks](https://code.claude.com/docs/en/hooks-guide) — événements du cycle de vie des hooks, application contrainte contre recommandation de `CLAUDE.md`, exemples d'usage
- [Connect Claude Code to tools via MCP](https://code.claude.com/docs/en/mcp) — portée projet de `.mcp.json` contre portée locale ou utilisateur de `~/.claude.json`
- [Run parallel sessions with worktrees](https://code.claude.com/docs/en/worktrees) — `--worktree`, `.worktreeinclude`, `isolation: worktree` pour un sous-agent
- [AGENTS.md](https://agents.md/) — la page de spécification du standard ouvert lui-même
