---
created: 2026-09-08T17:38:40Z
updated: 2026-11-09T17:14:13Z
---

> **Premier apprentissage :** 2026-09-08 15:30:00
> **Dernière mise à jour :** 2026-09-08 15:30:00

## Contexte

Un véritable backend multi-services a traversé plusieurs tours de critique avant que son découpage interne ne se stabilise en quelque chose qui vaille d'être réutilisé tel quel sur le *prochain* service backend, au lieu d'être re-dérivé (en refaisant les mêmes erreurs déjà corrigées) à chaque fois. Ce fichier est la version généralisée et indépendante du projet de cette structure établie — extraite des notes d'apprentissage internes d'un projet et de la compétence de génération de structure qui l'accompagne, pour qu'un nouveau projet puisse démarrer un service backend déjà à la forme « établie » plutôt qu'à la forme « première tentative, sur le point d'être critiquée ».

Ceci complète `01-documentation-structure-template.md` : ce fichier-là parle de la couche *documentaire* qui se trouve au-dessus d'un projet ; celui-ci parle de la couche de *code interne* qui se trouve à l'intérieur d'un service backend. Employez-le dès que `SOLUTION_DESIGN.md` §4 / §6 a décidé qu'un service a besoin d'une véritable structure interne (et non d'un script d'un seul fichier), avant d'écrire la première ligne du code source de ce service.

## Comment cela a été appris

**Le déclencheur :** un deuxième service backend du même projet avait besoin de partager une table de base de données avec le premier. Décider *comment* a forcé une véritable question d'architecture, documentée par recherche — dupliquer la couche de correspondance d'accès aux données dans chaque service, ou en extraire un paquet partagé — ce qui exigeait à son tour que le découpage lui-même soit déjà suffisamment fondé pour qu'on puisse raisonner proprement dessus. C'est cette mise sous pression qui a fait émerger la plupart des règles ci-dessous ; elles n'ont pas été conçues d'avance, elles ont été corrigées jusqu'à prendre leur forme.

**Le chemin :** le premier service backend n'a pas démarré avec cette structure — il a traversé de véritables tours de critique qui ont attrapé : de la logique métier dépendant accidentellement d'un type d'ORM propre à un framework au lieu d'un simple objet de domaine ; une hiérarchie d'exceptions éclatée entre les couches, qui rendait flou laquelle avait le droit de décider un code de statut HTTP ; et un réflexe de « il suffit d'ajouter le champ au modèle » qui faisait fuir une préoccupation de la couche de persistance (une colonne de base de données) dans du code qui ne devrait jamais voir qu'un concept de domaine. Chacun de ces points a été corrigé une fois, puis écrit comme une règle pour que la correction n'ait pas à se reproduire sur le service suivant. Quand un deuxième service a eu besoin de la même base, le choix entre « dupliquer la correspondance » et « partager un paquet » a été résolu en pesant un compromis concret (risque de dérive de schéma de la duplication contre conflit de convention d'outillage d'un paquet partagé) plutôt que pris par défaut — voir le journal des décisions pour la façon dont ce cas précis a été raisonné.

**Points de vigilance :**
- Cette structure mérite son coût sur un service doté d'une véritable logique métier et de plus de deux ou trois entities. Un service utilitaire à un seul point d'entrée n'a pas besoin de quatre couches — ne l'imposez pas à quelque chose qui n'a pas la complexité pour le justifier.
- La règle de dépendance à sens unique (ci-dessous) est facile à énoncer et facile à violer par accident la première fois qu'un raccourci « juste cette fois » paraît pratique — par exemple importer un modèle d'ORM directement dans un gestionnaire de route pour économiser une conversion. Chacun de ces raccourcis, pris une fois, devient très difficile à retrouver et à défaire plus tard, une fois qu'une douzaine d'autres routes ont copié le même raccourci.
- Décider s'il faut dupliquer une couche de correspondance d'accès aux données ou la partager comme paquet entre services est un véritable compromis, peu évident, et non une valeur par défaut — voir la sous-section « Partager l'accès aux données entre services » de la règle.

## La règle

### Les quatre couches, et la dépendance à sens unique

```
Entities  ←  Data Access Layer (DAL)  ←  Business Logic Layer (BLL)  ←  couche API
```

Les dépendances pointent **dans un seul sens** ; de gauche à droite n'est jamais permis :

- **Entities** — des objets de domaine simples (une dataclass, un modèle Pydantic employé comme type de domaine, ou l'équivalent dans votre langage). Aucun import de framework, aucune classe de base d'ORM, aucune connaissance du fait qu'une base de données existe. C'est à cela que toutes les autres couches pensent réellement.
- **Data Access Layer (DAL)** — la *seule* couche autorisée à importer la bibliothèque d'ORM ou de base de données. Elle fait la correspondance entre la représentation de persistance du framework (par exemple une classe mappée SQLAlchemy) et une Entity simple, et expose des fonctions ou des méthodes qui ne prennent et ne renvoient que des Entities — jamais le type de ligne de l'ORM. Gardez la vraie classe mappée privée au module (par exemple préfixée `_UserRow` ou équivalent) pour que rien, hors de cette couche, ne soit même tenté de l'importer directement.
- **Business Logic Layer (BLL)** — toutes les règles métier, la validation et l'orchestration des appels à la DAL. Prend des Entities, renvoie des Entities — jamais un DTO, jamais un type d'ORM. C'est ici que se décide « cette action peut-elle avoir lieu », ni dans la couche API ni dans la DAL.
- **Couche API** — la gestion des requêtes et des réponses, uniquement. Convertit une requête entrante en ce dont la BLL a besoin, appelle la BLL, convertit le résultat Entity de la BLL en une forme de réponse (un DTO). Ne contient aucune règle métier propre.

**Pourquoi un seul sens, et pas un raccourci « juste cette fois »** : dès l'instant où un gestionnaire de route importe directement un modèle d'ORM, ou que la BLL commence à renvoyer une ligne de base de données, tout l'intérêt de la frontière a disparu — la couche censée être interchangeable et testable en isolation dépend désormais en silence de la chose dont elle était isolée. C'est de loin la façon la plus courante dont cette structure s'érode ; traitez toute demande d'exception comme un signal qu'il faut chercher plus sérieusement la bonne couche, et non comme un cas particulier pragmatique.

### Les DTO vivent à la frontière, pas au milieu

Un DTO (*Data Transfer Object* — la forme d'un corps de requête ou d'une charge de réponse) appartient à la couche API seulement. Il existe pour définir le *contrat réseau*, lequel a le droit de différer de la forme interne de l'Entity (noms de champs différents, sous-ensemble de champs, champ calculé). Ne laissez jamais un DTO fuir dans la BLL ni dans la DAL — ces couches ne voient jamais que des Entities.

### Exceptions : un seul fichier à plat, nommées sémantiquement, mises en correspondance en un seul endroit

- Gardez les classes d'exception dans un unique fichier à plat (par exemple `core/exceptions.py`), et non éclatées par couche ou par fonctionnalité. Nommez-les d'après la signification métier de l'échec (`InvalidCredentialsError`, `DuplicateEmailError`), jamais d'après la couche qui les a levées (`DAL_NotFoundError`) — un appelant ne devrait pas avoir besoin de savoir quelle couche a échoué pour comprendre ce qui a mal tourné.
- Faites correspondre chaque exception à un statut HTTP (ou à la réponse équivalente au niveau du transport) en exactement un endroit (par exemple `core/exception_handlers.py`). Aucun autre fichier ne devrait jamais décider d'un code de statut à partir d'un type d'exception — cette décision appartient à un seul endroit pour qu'elle ne puisse pas dériver vers deux réponses différentes pour la même exception.
- Il est acceptable, et souvent correct, qu'une exception couvre plus d'une cause sous-jacente quand l'appelant ne doit pas pouvoir les distinguer (par exemple une unique exception générique « identifiants invalides » couvrant à la fois « mauvais mot de passe » et « jeton expiré », pour qu'un appelant ne puisse pas se servir de la précision de l'erreur pour énumérer quelle partie du contrôle d'authentification a échoué).

### Partager l'accès aux données entre services

Dès l'instant où deux services indépendants doivent lire ou écrire le même magasin de données sous-jacent, il y a un véritable choix, et non une valeur par défaut :

| Option | Quand c'est le bon choix | Le coût réel |
|---|---|---|
| **Dupliquer la correspondance d'accès aux données** dans chaque service (chaque service définit son propre modèle de couche DAL pour la table partagée) | Les services sont censés rester déployables indépendamment, chacun avec sa propre configuration de dépendances et d'environnement, et le schéma de la table partagée change rarement et de façon prévisible (possédé par l'historique de migrations d'exactement un service) | Risque de dérive de schéma si les correspondances dupliquées ne sont pas maintenues en phase — à atténuer par un propriétaire unique et clair du schéma et des migrations, et un commentaire dans chaque copie pointant vers ce propriétaire |
| **Extraire un paquet partagé** (une bibliothèque partagée dont les deux services dépendent) | Les services partagent déjà une configuration de gestion de dépendances (un espace de travail de type monodépôt, un environnement virtuel ou un fichier de verrouillage commun), ou le schéma partagé change assez souvent pour que la duplication dérive immédiatement | Cela signifie généralement de rassembler les deux services sur un même environnement et un même fichier de verrouillage — un coût réel si la convention de votre projet est un environnement indépendant par service |

Quel que soit le choix retenu, consignez la décision sous forme d'entrée d'ADR dans `SOLUTION_DESIGN.md` §14 — c'est exactement le genre de choix qui paraît arbitraire avec le recul si le compromis qui a été pesé n'est pas enregistré.

### Une forme de dossiers minimale pour un service backend

```
<service>/
├── app/
│   ├── main.py                 <- point d'entrée de l'application / amorçage du serveur
│   ├── core/
│   │   ├── config.py           <- chargement des réglages et de l'environnement
│   │   ├── exceptions.py       <- fichier à plat, une classe par échec métier
│   │   └── exception_handlers.py  <- le seul endroit où les exceptions deviennent un statut de réponse
│   ├── entities/                <- objets de domaine simples, aucun import de framework
│   ├── dal/                     <- la seule couche autorisée à importer la bibliothèque d'ORM ou de BD
│   ├── bll/                     <- règles métier, ne prend et ne renvoie que des Entities
│   └── api/
│       └── v1/
│           └── dto/             <- formes de requête et de réponse, couche API seulement
└── <manifeste de dépendances, dossier de migrations, etc. selon votre pile>
```

Un service fraîchement généré devrait avoir une infrastructure fonctionnelle (`core/`, la mise en place de la connexion à la base dans la DAL, un routeur API vide) mais **aucun** fichier `entities/`, `dal/`, `bll/` ni `dto/` pour l'instant — ce sont du vrai travail fonctionnel, ajouté par unité de travail (par user story), et non une partie de la génération de structure. Les construire avant un besoin réel produit du code mort qu'il faut maintenir sans jamais l'exercer.

### Un piège de concurrence à vérifier dès l'instant où un deuxième écrivain apparaît

Si plus d'un processus ou service va écrire dans la même base de données légère sur fichier (par exemple SQLite), ne supposez pas qu'un réglage de concurrence documenté (par exemple « nous utilisons le mode WAL ») est réellement en vigueur — vérifiez-le directement (interrogez le réglage réel à l'exécution) plutôt que de faire confiance à un commentaire ou à un tableau de pile technique. Une configuration à un seul écrivain ne fait jamais apparaître l'écart ; cela ne devient un vrai risque de correction qu'à l'instant où un deuxième écrivain rejoint, c'est-à-dire exactement au moment où c'est le plus facile à manquer, parce que rien dans l'ajout du second service ne *ressemble* à un changement de base de données.

### Un piège d'origine croisée à vérifier dès l'instant où un deuxième frontend, sur une origine distincte, apparaît

Si un frontend de navigateur appelle ce backend depuis une origine différente (port ou domaine différent), une vérification côté backend seulement (un client HTTP en ligne de commande) n'attrapera pas une configuration CORS manquante — le préambule CORS et son application sont purement côté navigateur, invisibles pour tout client non navigateur. Le seul contrôle fiable est un véritable test depuis un navigateur (un script de navigateur sans interface, ou un parcours manuel) pilotant le vrai frontend contre le vrai backend.

## Erreurs courantes

| Erreur | Pourquoi cela arrive | Correctif |
|---|---|---|
| Importer la classe mappée par l'ORM directement dans un gestionnaire de route « juste pour économiser une conversion » | Sur le moment, cela ressemble à du code cérémoniel inutile | Convertissez toujours vers et depuis l'Entity à la frontière de la DAL, même quand cela paraît redondant pour un ensemble de champs trivial — ce code cérémoniel est ce qui garde la frontière réelle |
| Laisser un nom ou une forme de champ de DTO fuir dans la logique propre de la BLL (par exemple en testant un champ facultatif du DTO au lieu de celui de l'Entity) | Le DTO est déjà dans la portée du gestionnaire d'API, il paraît pratique de le passer tel quel | Convertissez DTO → Entity avant d'appeler la BLL, toujours, même pour une requête à un seul champ |
| Éclater les classes d'exception par couche (`DAL_NotFoundError`, `BLL_NotFoundError`) | Cela donne l'impression de refléter proprement l'architecture | Nommez les exceptions d'après la signification métier de l'échec, pas d'après la couche — un fichier à plat, une signification par classe |
| Supposer qu'un réglage de concurrence ou de CORS documenté est réellement implémenté, parce qu'il est écrit dans un document de configuration ou d'architecture | La documentation décrit une intention, et une intention se confond facilement avec un fait vérifié | Vérifiez le comportement à l'exécution directement (interrogez le réglage réel, lancez le vrai contrôle depuis un navigateur) dès l'instant où un deuxième service ou une deuxième origine rejoint, ne faites pas confiance au document seul |

## Journal des décisions — séquence des changements

1. **Premier service backend construit** — le découpage en quatre couches (Entities / DAL / BLL / API) et la convention du fichier d'exceptions à plat adoptés après que de véritables critiques ont attrapé des violations de frontière dans un brouillon antérieur.
2. **Le deuxième service backend a eu besoin de partager une table avec le premier** — résolu via le compromis « Partager l'accès aux données entre services » ci-dessus : la correspondance de couche DAL a été dupliquée plutôt que d'extraire un paquet partagé, précisément parce que la convention du projet était un environnement de dépendances indépendant par service, et qu'un paquet partagé aurait exigé de rassembler les deux sur un seul environnement.
3. **La construction du deuxième service a fait apparaître deux véritables lacunes, et non des décisions** : un réglage de concurrence de base de données documenté mais non implémenté, et une configuration CORS manquante attrapée seulement par un vrai test depuis un navigateur après qu'un contrôle en ligne de commande était passé proprement — tous deux généralisés en les deux sous-sections de pièges ci-dessus.
