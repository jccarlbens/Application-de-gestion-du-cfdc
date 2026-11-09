---
created: 2026-09-16T19:40:29Z
updated: 2026-11-09T17:14:13Z
---

# L'architecture, expliquée

**Répond à :** comment le code est-il découpé, pourquoi ainsi, et qu'est-ce que chaque fichier a le droit d'importer ?
**À lire :** une fois, avant d'écrire le premier fichier source de l'une ou l'autre moitié. Puis gardez-le ouvert pendant que vous écrivez les dix suivants.

C'est le seul document du kit qui vous donne des réponses au lieu de questions.
Tout le reste sous `project-docs/` vous demande de réfléchir — `PRD.md` demande ce que vous construisez, `SOLUTION_DESIGN.md` demande comment.
Ce fichier-ci dit : *voici une structure qui fonctionne, voici pourquoi elle fonctionne, et voici ce qu'elle coûte.*

**Vous pouvez remplacer n'importe quelle partie.** Ce que vous ne pouvez pas faire, c'est la laisser implicite.
Une architecture que personne n'a écrite n'est pas une architecture plus simple ; c'est le même nombre de décisions, prises chacune une fois par celui qui a touché le fichier le premier, et jamais écrites là où la personne suivante peut les trouver.

---

## Partie 0 — L'idée unique

L'essentiel de ce qui suit est une conséquence d'une seule règle.
Robert C. Martin l'appelle la **règle de dépendance** (*Dependency Rule*), et l'énonce en une phrase :

> Les dépendances du code source ne doivent pointer que vers l'intérieur.
> Rien dans un cercle intérieur ne peut savoir quoi que ce soit de quelque chose situé dans un cercle extérieur.

Alistair Cockburn est arrivé au même endroit par un autre chemin, et c'est sa formulation qui fait tout comprendre :

> L'asymétrie à exploiter n'est pas celle entre les côtés *gauche* et *droit* de l'application, mais celle entre l'*intérieur* et l'*extérieur*.

Son propos est que l'interface utilisateur et la base de données sont **la même sorte de chose** : toutes deux sont externes, toutes deux sont remplaçables, et toutes deux chercheront à s'étaler à travers vos règles métier si vous les laissez faire.
Un framework web et un pilote Postgres ne sont pas des opposés — ce sont deux adaptateurs sur deux ports de la même machine.

### Ce que la règle vous achète

- **Vous pouvez tester le milieu sans rien démarrer.** Pas de serveur, pas de base de données, pas de navigateur. Si vos règles métier ont besoin d'un Postgres en fonctionnement pour être exercées, c'est qu'elles ne sont pas isolées de Postgres.
- **Vous pouvez remplacer une frontière.** Échanger SQLite contre Postgres, ou REST contre un consommateur de file de messages, touche une seule couche.
- **Un bogue a une adresse.** Quand une sortie est fausse, vous pouvez demander *quelle couche a le droit de savoir cela ?* et aller là.

### Le test qui compte vraiment

Ne mesurez pas votre architecture à son diagramme de dossiers. Mesurez-la à cette question :

> **Prenez n'importe quel fichier au hasard. Pouvez-vous dire, sans regarder, de quels dossiers exactement il a le droit d'importer ?**

Si oui, vous avez une architecture. Si cela dépend du fichier, vous avez une disposition de dossiers.

### Et une règle que personne ne vérifie est une préférence

C'est la partie que la plupart des projets sautent, et c'est celle qui décide si la structure survit au contact d'une échéance.

**Les deux moitiés de ce kit font appliquer leur règle de dépendance par une machine.**
Le backend le fait avec un test qui analyse chaque import et fait échouer la compilation (`tests/unit/test_architecture.py`).
Le frontend le fait avec un linter d'architecture (Steiger).
Ni l'un ni l'autre ne compte sur la mémoire de quiconque.

La première fois que quelqu'un importe le modèle d'ORM directement dans un gestionnaire de route « juste pour économiser une conversion », la frontière a disparu — et elle aura disparu en silence, parce que tout continue de fonctionner. Dix routes plus tard, c'est irrécupérable. Un contrôle, c'est ce qui transforme cela d'une affaire de jugement en une compilation rouge.

---

## Partie 1 — Le backend : quatre couches, un seul sens

```
entities  ←  dal  ←  bll  ←  api
   ↑                          ↑
   └──────── core/ ───────────┘   (config, journalisation, exceptions : disponibles pour tous)
```

Les flèches se lisent **« est importé par »**. Les dépendances vont de droite à gauche, et jamais de gauche à droite.

**Cette forme a un nom, et ce nom est N-Layer** — une architecture en couches, dans laquelle chaque couche importe celle du dessous. Lisez la partie 1 pour savoir ce que fait chaque dossier, puis la partie 2 pour savoir d'où vient la règle et comment s'appelle l'agencement plus strict qui se trouve à côté.

**Soyez précis sur ce nom, parce qu'une étiquette nue est injuste envers cette structure.** La Clean Architecture stricte vous demande trois choses. Cette forme en fait deux, et les fait appliquer toutes les deux par des tests : les entities sont au plus profond et ne connaissent aucun framework, et exactement une couche sait qu'un ORM existe. Elle décline la troisième — `bll` importe `dal` directement plutôt qu'une interface dont elle serait propriétaire. **Cette unique différence est ce qui fait de ceci du N-Layer et non de la Clean**, et la partie 2 vous donne la question qui décide si vous devriez la combler.

Si vous voulez la version en un paragraphe de l'ensemble : **les choses qui changent lentement vont au milieu, les choses qui changent vite vont à la frontière, et rien au milieu n'a le droit de nommer quoi que ce soit à la frontière.**

### `entities/` — des objets de domaine simples

Les choses *dont parle* votre produit : un `User`, un `Order`, une `Invoice`.

- Une dataclass, ou un modèle Pydantic employé comme type de domaine. Rien de plus.
- **Aucun import de framework. Aucune classe de base d'ORM. Aucune connaissance du fait qu'une base de données existe.**
- C'est ce que toutes les autres couches se passent et avec quoi elles pensent.

Si `entities/` importe SQLAlchemy, le cercle le plus intérieur dépend désormais du plus extérieur, et chacun des bénéfices ci-dessus disparaît d'un coup.

### `dal/` — la couche d'accès aux données

**La seule couche de toute la base de code autorisée à importer l'ORM.**

- Elle fait la correspondance entre la représentation de persistance (une classe mappée SQLAlchemy) et une entity simple.
- Ses fonctions **prennent des entities et renvoient des entities** — jamais une ligne mappée.
- Gardez la classe mappée privée au module : nommez-la `_UserRow`, pour que rien à l'extérieur ne soit même tenté.

C'est le motif Repository, et son but a un nom : **l'ignorance de la persistance**. Le reste de l'application ne sait pas *comment* une chose est stockée, seulement qu'elle peut être obtenue et déposée.

### `bll/` — la couche de logique métier

Chaque règle, chaque validation, chaque morceau d'orchestration portant sur plus d'un appel à `dal/`.

- Prend des entities, renvoie des entities. **Jamais un DTO. Jamais un type d'ORM.**
- C'est ici que se décide *« est-ce permis ? »* — ni dans la route, ni dans la DAL.
- Si vous vous demandez où va un morceau de logique et que la réponse est « eh bien, la route a déjà la donnée », la réponse reste ici.

### `api/` — la frontière

Requête en entrée, réponse en sortie. Rien d'autre.

- Convertir le corps de la requête entrante (un DTO) en ce dont la BLL a besoin.
- Appeler la BLL.
- Convertir l'entity que la BLL renvoie en un DTO de réponse.
- **Aucune règle métier.** Une route qui contient un `if` portant sur votre domaine est une route qui a volé le travail de la BLL.

### Les DTO vivent à la frontière et nulle part ailleurs

Un **DTO** (*Data Transfer Object*) est la forme d'un corps de requête ou d'une charge de réponse. C'est votre **contrat réseau** — la promesse que vous faites à qui vous appelle.

Il a délibérément le droit de différer de votre entity : noms de champs différents, sous-ensemble de champs, champ calculé, relation aplatie. Cette liberté *est le but*. Votre modèle interne doit rester libre de changer sans casser tous les clients.

**Un DTO ne doit jamais atteindre la BLL ni la DAL.** À l'instant où une logique métier se ramifie sur un champ facultatif d'un DTO, votre format réseau est devenu votre modèle de domaine, et vous ne pouvez plus changer l'un ou l'autre séparément.

### Pourquoi `api/v1/`, et ce que le `v1` promet réellement

La génération de structure place les routes sous `app/api/v1/`, avec les DTO à `app/api/v1/dto/`. Ce n'est pas décoratif.

**Un numéro de version est une promesse qu'un client écrit aujourd'hui continuera de fonctionner demain.** Dès que quelque chose d'autre consomme votre API — un frontend que vous possédez aussi, une application mobile, une autre équipe — vous ne contrôlez plus le moment où les appelants se mettent à jour. Le versionnage vous donne un endroit où mettre un changement qui, autrement, les casserait : `v2` apparaît, `v1` continue de fonctionner, les clients migrent à leur propre rythme.

Ce qui compte comme cassant, et exige donc une nouvelle version : retirer un champ, en renommer un, restreindre un type, rendre obligatoire un champ facultatif, changer la signification d'un code de statut. Ce qui ne l'est pas : **ajouter** un champ facultatif, ajouter un point d'entrée, ajouter une valeur d'énumération que les clients sont priés d'ignorer quand elle est inconnue.

**La raison structurelle pour laquelle cela vit dans le nom du dossier** : parce que `dto/` se trouve *à l'intérieur* de `v1/`, un DTO de v2 est un fichier différent plutôt qu'une modification d'un fichier partagé. Deux versions peuvent se contredire sans un seul `if version == 1` quelque part dans votre code. C'est ce qui empêche le versionnage de pourrir en un tas de conditions.

**Quand cela paye — la question à se poser :** *combien d'appelants peuvent rester en retard sur un déploiement ?*

Si la réponse est ne serait-ce qu'un seul que vous ne contrôlez pas — une application mobile, une autre équipe, un point d'entrée public — commencez avec `v1` dès aujourd'hui. Cela coûte un dossier maintenant, là où ajouter du versionnage à une API qui n'en a jamais eu coûte la migration de chaque appelant dont vous ignoriez l'existence.

Si la réponse est véritablement zéro — un seul frontend, dans le même dépôt, sur la même étiquette git, déployé dans le même souffle — alors le numéro de version est une promesse faite à personne, et le dossier est une cérémonie que vous taperez pendant des années. **L'implémentation de référence de ce kit répond zéro, et n'a pas d'`api/v1/`.** La partie 2 § *Les quatre recommandations que l'implémentation de référence de ce kit rejette* en donne le tableau complet.

### Exceptions : un fichier à plat, des noms métier, mises en correspondance en un seul endroit

- Gardez les classes d'exception dans **un seul fichier à plat** (`core/exceptions.py`) — pas éclatées par couche, pas par fonctionnalité.
- Nommez-les d'après **ce qui a échoué en termes métier** : `InvalidCredentialsError`, `DuplicateEmailError`. Jamais `DalNotFoundError`. Un appelant ne devrait pas avoir à savoir quelle couche a cassé pour comprendre ce qui a mal tourné.
- Faites correspondre chaque exception à un statut HTTP en **exactement un endroit** (`core/exception_handlers.py`). Aucun autre fichier ne décide d'un code de statut à partir d'un type d'exception — sinon le même échec reçoit deux réponses différentes dans deux routes différentes, et personne ne s'en aperçoit pendant des mois.
- Qu'une exception couvre plusieurs causes est souvent *correct* : un unique `InvalidCredentialsError` pour « mauvais mot de passe » et « jeton expiré » à la fois est délibéré, parce qu'un appelant capable de les distinguer peut énumérer votre contrôle d'authentification.

**Quand cela paye — la question à se poser :** *combien d'exceptions métier, levées à travers combien de routes ?* Un fichier à plat et une table de gestionnaires payent dès que le même échec peut arriver par plusieurs routes et doit produire le même statut à chaque fois. Avec trois exceptions, chacune levée en un seul endroit et chacune traitée délibérément là où elle est attrapée, une table centrale est un deuxième endroit où chercher quelque chose qui n'a jamais été en deux endroits. **L'implémentation de référence de ce kit en a trois, et pas de `core/exceptions.py`** — la partie 2, encore.

### Application contrainte

Écrivez le test avant d'en avoir besoin. **Le premier jour, c'est environ quarante lignes**, et ces quarante-là font déjà la différence entre une architecture et une intention :

```python
# tests/unit/test_architecture.py — parcourt chaque import de app/ et vérifie le sens
FORBIDDEN = {
    "entities": ("dal", "bll", "api", "sqlalchemy", "fastapi"),
    "dal":      ("bll", "api"),
    "bll":      ("api", "sqlalchemy"),
}
```

Analysez les imports de chaque module avec `ast`, déduisez sa couche de son chemin, et faites échouer sur toute correspondance.

**Ensuite il grandit, et cette croissance est la partie intéressante.** Le projet de référence depuis lequel ce kit a été écrit exécute aujourd'hui une vingtaine de règles depuis ce seul fichier, et presque chacune d'elles a été ajoutée le jour où quelque chose a failli mal tourner. **Vous n'écrivez pas celles-là le premier jour.** Vous écrivez celle ci-dessus, et vous ajoutez chacune des autres quand elle devient vraie de votre projet pour la première fois :

| Ce que cela vérifie | Pourquoi cela a été ajouté |
|---|---|
| Chaque fichier appartient à une couche connue | un nouveau dossier de premier niveau est une décision de découpage, et elle devrait être délibérée plutôt que découverte |
| Les imports respectent le sens, couche par couche | la règle elle-même |
| Rien n'importe la couche de présentation | l'API est l'anneau le plus extérieur ; tout ce qui en dépend inverse le diagramme entier |
| La couche métier n'importe jamais l'ORM | la règle qui rend la DAL digne d'être construite |
| Le type de session de l'ORM n'est nommé que dans une couche | une session passée vers le haut, c'est l'ORM qui fuit, sans l'import qui l'aurait montré |
| Seule l'unité de travail termine une transaction | un commit est une décision de stockage, et elle appartient là où le stockage se décide |
| Aucun type de ligne stockée n'est nommé hors de la DAL | la classe mappée est la forme sur le disque, pas une forme que quiconque d'autre se passe |
| Le SDK du fournisseur n'est importé que dans un dossier | pour que changer de fournisseur soit un travail borné plutôt que de l'archéologie |
| La bibliothèque de validation n'apparaît que dans le dossier des DTO | le format réseau se décide en un seul endroit |
| Les entities n'importent rien d'autre que la configuration | l'anneau le plus intérieur ; s'il prend des dépendances, le découpage est à l'envers |
| Les entities ne nomment aucun concept de stockage | la façon dont une chose est sauvegardée n'est pas l'affaire de cette chose |
| Les entities ne sérialisent rien — pas d'`as_dict` | les entities décrivent, les DTO exposent |
| Rien de coûteux n'est construit au moment de l'import | pour que n'importe quel module puisse être importé dans un test sans démarrer une base de données ou un client |
| Chaque couche peut être importée la première, seule | exécuté dans un sous-processus sans rien d'autre de chargé : le détecteur d'import circulaire le moins coûteux qui existe |
| Les préfixes de couche n'atteignent jamais rien que lise un utilisateur | `Dal`, `Bll` et `Ent` nomment nos classes, pas nos concepts |

**Cinq d'entre elles valent d'être volées avant que vous pensiez en avoir besoin** : rien n'importe l'API, la couche métier n'importe jamais l'ORM, le type de session reste dans une seule couche, rien n'est construit au moment de l'import, et chaque couche s'importe seule. Elles font une dizaine de lignes chacune, et chacune attrape une erreur invisible en relecture et coûteuse à défaire.

Le raisonnement complet derrière ce découpage, y compris le compromis du partage d'une DAL entre deux services, est dans `project-docs/learnings/03-backend-layered-architecture-template.md`. Le *comment* — les dossiers, le code d'amorçage, les commandes — est la compétence `scaffold-backend-service`.

---

## Partie 2 — Comment cela s'appelle, et comment cela ne s'appelle pas

**La structure de la partie 1 est du N-Layer. La Clean Architecture est la chose plus stricte qui se tient à côté**, et les deux sont assez proches pour que des projets revendiquent couramment la seconde en construisant la première — généralement sans s'en apercevoir, parfois dans le même document.

Toutes deux appartiennent à une même famille, et c'est cette famille qu'il faut chercher quand vous voulez en lire davantage. Cette partie vous donne cette famille, puis l'unique mécanisme qui sépare son membre strict de son membre relâché, puis les quatre endroits où le projet de référence de ce kit a regardé la version stricte et a dit non.

**Cette dernière section est celle à lire deux fois.** Quatre règles valent moins pour vous que les quatre questions qui les décident, parce que votre projet n'est pas celui-ci.

### Une idée, quatre noms, vingt ans

La même architecture a été atteinte indépendamment plusieurs fois, et chaque arrivée lui a donné un nom différent. Ce ne sont pas des approches concurrentes, et vous n'avez pas à choisir entre elles :

| Année | Nom | Qui | Ce que cela a ajouté |
|---|---|---|---|
| 2005 | **Architecture hexagonale**, plus tard **Ports & Adapters** | Alistair Cockburn | l'intuition que l'interface utilisateur et la base de données sont la même sorte de chose — toutes deux à l'extérieur |
| 2008 | **Onion Architecture** | Jeffrey Palermo | l'image concentrique, et l'argument tiré du *taux de changement* : la technologie d'accès aux données change tous les quelques années, elle ne doit donc pas être au centre |
| 2012 | **Clean Architecture** | Robert C. Martin | la consolidation, et la règle de dépendance ramenée à une seule phrase citable |

C'est la formulation de Palermo qui vaut d'être emportée, parce qu'elle explique *pourquoi* la règle pointe dans ce sens : **mettez au centre les choses qui changent lentement, et à la frontière celles qui changent vite.** Vos règles métier survivront à votre base de données, à votre framework web et probablement à votre langage. Structurez le code pour que cela soit possible.

C'est aussi pourquoi `entities/` est au plus profond. Non parce que c'est important en un sens abstrait — parce que c'est la partie que vous voulez le moins réécrire quand tout autour est remplacé.

### La seule chose qui sépare les deux, et qu'un diagramme ne peut pas montrer

**L'inversion de dépendance.** C'est le mécanisme, c'est la seule différence structurelle entre N-Layer et Clean, et c'est la partie que la plupart des gens manquent quand ils recopient le diagramme de dossiers.

Voici le problème qu'elle résout. À l'**exécution**, le contrôle s'écoule vers l'*extérieur* : la BLL a besoin d'un utilisateur, donc la DAL lance une requête, donc le pilote de base de données ouvre une socket. C'est inévitable — la logique métier a réellement besoin de la base de données.

Mais si la BLL *importe* la DAL pour faire cela, la dépendance **du source** pointe vers l'extérieur, et la Clean Architecture stricte dit que la règle est brisée. Que cela importe ou non à votre projet est l'objet de la section suivante. Voici à quoi ressemble le fait de combler cet écart.

- La couche **intérieure** déclare ce dont elle a besoin, sous forme d'une interface dont elle est propriétaire : `UserRepository`, avec un `find_by_email` qui prend et renvoie des entities.
- La couche **extérieure** l'implémente : `DalUser` satisfait cette interface en se servant de SQLAlchemy.
- Quelque chose à l'extrême frontière — la **racine de composition**, généralement là où votre application démarre — lui passe l'implémentation concrète.

En Python, l'interface est un `Protocol`, et elle vit dans la couche intérieure parce que c'est la couche intérieure qui en est propriétaire :

```python
# bll/bll_ports.py - déclaré par la couche métier, implémenté par rien en elle
from typing import Protocol
from entities.ent_user import EntUser

class UserRepository(Protocol):
    async def find_by_email(self, email: str) -> EntUser | None: ...
    async def save(self, user: EntUser) -> None: ...
```

```python
# bll/bll_registration.py - nomme le port, et ne nomme jamais `dal`
class BllRegistration:
    def __init__(self, users: UserRepository) -> None:
        self._users = users
```

```python
# composition.py - le seul fichier autorisé à savoir que les deux côtés existent
from dal.dal_user import DalUser          # satisfait structurellement UserRepository
BllRegistration(users=DalUser(session))
```

`bll/` nomme désormais une interface dont elle est propriétaire et ne nomme jamais SQLAlchemy — ni `dal`. Le contrôle s'écoule toujours vers l'extérieur à l'exécution ; la dépendance du source pointe vers l'intérieur. **La dépendance à la compilation et le sens d'appel à l'exécution sont deux choses différentes, et inverser l'une sans l'autre est toute l'astuce.**

Deux choses à savoir avant d'y recourir.

**Un `Protocol` est structurel, donc `DalUser` ne mentionne jamais `UserRepository`** — il a simplement les bonnes méthodes. C'est un véritable avantage sur une classe de base abstraite, parce que la couche extérieure n'a pas non plus à importer l'intérieure. C'est aussi le piège : **rien ne vérifie que la correspondance tient encore, à moins qu'un vérificateur de types ne s'exécute.** Ajoutez `mypy` ou `pyright` à vos contrôles, sinon le port est un commentaire doté d'une syntaxe.

**Le test qui vous dit si vous l'avez réellement fait :** pouvez-vous tester unitairement `bll/` sans aucune base de données en fonctionnement, en lui passant un faux objet ? Si oui, vous avez inversé la dépendance. Si vous avez dû démarrer SQLite pour tester une règle métier, vous avez dessiné le diagramme et n'avez pas construit l'architecture.

**Le projet de référence de ce kit échoue à ce test exprès.** La section suivante dit pourquoi.

### Les quatre recommandations que l'implémentation de référence de ce kit rejette

Chaque recommandation de la partie 1 est un vrai conseil. Le projet de référence de ce kit — celui depuis lequel tous ces documents ont été écrits — n'en suit quatre pas du tout.

**Ce n'est pas un aveu, c'est tout l'objet de la section.** Un document qui ne fait que lister des règles vous enseigne quatre règles. Un document qui vous montre où une règle a été déclinée, et sur quelles preuves, vous apprend à décider.

| La recommandation | La question qui la décide | La réponse du projet de référence | Verdict là-bas |
|---|---|---|---|
| **Inverser la jointure `bll` → `dal`**, avec un Protocol dont la BLL est propriétaire | Combien d'implémentations existeront *en même temps* ? | Une. Échanger SQLite contre Postgres touche un seul fichier dans `dal/` et rien au-dessus | Déclinée |
| **`api/v1/`** | Combien d'appelants peuvent rester en retard sur un déploiement ? | Zéro. Un frontend, même dépôt, même étiquette git, déployés ensemble | Déclinée |
| **`core/exceptions.py` et une table de gestionnaires** | Combien d'exceptions métier, levées à travers combien de routes ? | Trois, chacune levée en un seul endroit et chacune traitée délibérément là où elle est attrapée | Déclinée |
| **Alembic** | À quelle fréquence le schéma change-t-il, et qui d'autre lit le fichier ? | La base de données est un unique fichier jetable que le projet vous dit de supprimer | Déclinée |

**La forme de l'argument est la même dans les quatre cas, et c'est la partie qui se transpose :** chacune de ces choses est une abstraction qui ne paye que lorsqu'il y a *deux* de quelque chose — deux implémentations, deux appelants sur des cycles de livraison différents, deux douzaines d'exceptions, deux écrivains d'un même schéma. Avec un seul de chaque, vous payez le coût et ne récoltez aucun des bénéfices.

**L'inversion de dépendance est celle qui piège les gens, y compris les gens expérimentés.** Son bénéfice est réel. Simplement, avec une seule implémentation, vous en avez déjà l'essentiel par la seule **encapsulation** : la BLL ne sait toujours pas ce qu'est du SQL, elle passe toujours des entities en entrée et en sortie, et elle survit toujours à un changement de base de données sans être touchée. Ce que le Protocol ajoute *par-dessus cela*, c'est la possibilité de supprimer `dal/` et de pouvoir encore importer `bll/`. Demandez-vous donc quand vous feriez cela. Si la réponse est *« quand je teste unitairement la couche métier sans base de données »*, c'est une vraie réponse et vous devriez inverser. Si votre couche métier n'est jamais exercée que par des tests d'intégration contre un vrai fichier SQLite — le cas du projet de référence — alors le port est une cérémonie avec un diagramme attaché.

**Écrivez ce qui rouvrirait chaque décision.** Une décision consignée sans sa condition d'expiration devient du folklore : la personne suivante trouve la règle, ne trouve pas le raisonnement, puis soit lui obéit longtemps après qu'elle a cessé d'être vraie, soit la brise juste avant qu'elle ne compte. Consignez chacune comme un ADR avec un déclencheur énoncé — *une deuxième implémentation* ; *un appelant que nous ne déployons pas* ; *la dixième exception* ; *une base de données qu'on a promis de rendre à quelqu'un*. Quand le déclencheur se produit, la décision est rouverte exprès au lieu d'être découverte obsolète.

**Et remarquez ce que rien de tout cela n'autorise.** Décliner une abstraction n'est pas décliner la règle. Le projet de référence interdit toujours l'ORM au-dessus de la DAL, garde toujours les DTO hors de la couche métier, garde toujours les entities exemptes de framework, et fait appliquer les trois par des tests qui font échouer la compilation. **La règle de dépendance survit intégralement ; une seule jointure est laissée concrète.** YAGNI est un argument contre *la construction de l'abstraction*. Ce n'est jamais un argument contre *le tracé de la frontière*.

### L'objection du modèle anémique, et quoi en faire

Une critique vaut d'être affrontée de face, parce qu'elle est juste.

Vos `entities/` sont des dataclasses — des données sans comportement — et toute la logique vit dans `bll/`. Martin Fowler a baptisé cela le **modèle de domaine anémique** et le considère comme un anti-motif :

> Il n'y a presque aucun comportement sur ces objets, ce qui en fait à peine plus que des sacs d'accesseurs et de mutateurs.

Et l'accusation qui pique :

> Ils encourent tous les coûts d'un modèle de domaine, sans en produire aucun des bénéfices.

**Deux réponses honnêtes. Sachez laquelle vous donnez.**

1. **Pour la plupart des applications, ce marché est acceptable, et il faut le passer en le sachant.** Si vos règles sont surtout de la validation, de l'autorisation et de l'orchestration portant sur plusieurs choses stockées, elles n'appartiennent véritablement pas à un seul objet, et un modèle riche achète de la cérémonie plutôt que de la clarté. C'est le cas courant, et le choisir délibérément n'est pas la même chose que d'y dériver.

2. **Là où un comportement appartient clairement à une seule entity, mettez-le sur l'entity.** Rien dans cette architecture ne l'interdit — une méthode qui n'emploie que les champs propres de l'objet n'importe rien et ne brise aucune règle. `order.total()`, `invoice.is_overdue()`, `booking.overlaps(other)` appartiennent à l'objet. Déplacer ceux-là dans un service est la façon dont un modèle devient anémique : non pas par conception, mais une commodité à la fois.

**La règle empirique : si la logique n'a besoin que des données propres de cet objet, elle va sur l'objet. Si elle a besoin de la base de données, d'une autre entity ou du monde extérieur, elle va dans `bll/`.**

### Une note sur le Domain-Driven Design, pour que vous ne confondiez pas les deux

Vous rencontrerez le DDD dans presque tout ce qui s'écrit sur la Clean Architecture ; une courte section vaut donc d'être consacrée à garder les deux distincts.

**Ceci n'est pas du Domain-Driven Design, et vous ne devriez pas l'appeler ainsi.**

Le DDD est une discipline différente, portant sur *la façon dont on arrive à un modèle* par la conversation avec des experts du domaine. Son centre de gravité est stratégique — contextes délimités, sous-domaines, cartographie de contextes — et rien de cela n'est ici. Ce que cette architecture partage avec le DDD, ce sont deux de ses plus petits motifs tactiques : le **repository** (votre `dal/`) et l'**ignorance de la persistance** (vos `entities/`). Partager deux motifs avec une discipline ne fait pas de vous un praticien de cette discipline.

Evans lui-même a dit qu'il avait **trop insisté sur ces briques tactiques**, et que c'est la moitié stratégique qui compte et que les gens sautent. Ainsi, une base de code qui adopte les repositories et se dit DDD a adopté précisément la moitié que son auteur juge surpondérée. Nommez plutôt le découpage — « N-Layer », ou « Clean Architecture » si vous avez inversé la jointure — et laissez DDD signifier ce qu'il signifie.

**Recourez au vrai DDD quand les règles métier sont la partie difficile** — assurance, logistique, finance, facturation de soins — quand des experts du domaine se disputent sur le sens d'un mot et que différentes parties de l'organisation ont besoin de modèles différents du même nom commun. Pour une application CRUD dotée d'un modèle de permissions, cela produit des dossiers en forme de DDD sans aucun de ses bénéfices.

**Une idée du DDD vaut d'être volée quoi qu'il arrive, et vous l'avez déjà.** `GLOSSARY.md` — la règle selon laquelle les mots employés par les experts du domaine, les mots de vos conversations et les identifiants de votre code source doivent former **un seul vocabulaire** — c'est le *langage omniprésent* (*Ubiquitous Language*) du DDD, et c'est sans doute l'idée la plus précieuse du livre. Le kit l'impose structurellement : le glossaire est écrit avant le code, les termes de chaque user story doivent se résoudre en une entrée, et `check-project-docs` cherche les mots que vous avez abandonnés. Continuez de faire cela. Cela ne coûte presque rien et c'est là que se trouvait le vrai levier du DDD depuis le début.

---

## Partie 3 — Le frontend : Feature-Sliced Design

Le frontend emploie **Feature-Sliced Design (FSD)** : une méthodologie explicite, documentée à l'extérieur, dotée de sa propre spécification, de son linter et de son vocabulaire.

### Les couches

```
src/
  app/        providers, routeur, styles globaux, point d'entrée
  pages/      une slice par route — compose des widgets et des features
  widgets/    blocs composites autonomes (un en-tête, une barre latérale, un fil)
  features/   les choses que l'utilisateur *fait* — une action avec son interface et sa logique
  entities/   les noms communs du métier — l'utilisateur, la commande, le commentaire
  shared/     ui/ api/ lib/ config/ — réutilisable, indépendant du métier
```

Vous n'êtes pas obligé d'utiliser les six. **Leurs noms sont fixés, en revanche** — c'est ce qui rend la structure lisible pour quiconque connaît FSD. Une petite application peut démarrer avec seulement `app/`, `pages/`, `entities/` et `shared/`, puis faire pousser `features/` et `widgets/` quand elle en a besoin.

### Slices et segments

À l'intérieur de chaque couche sauf `app/` et `shared/`, le code est divisé en **slices** nommées d'après le domaine métier — `entities/user/`, `features/add-to-cart/`.

À l'intérieur de chaque slice, le code est divisé en **segments** nommés d'après leur rôle technique :

| Segment | Contient |
|---|---|
| `ui/` | les composants, le style, tout ce qui est visuel |
| `api/` | les requêtes vers le backend, et les types de ce qui en revient |
| `model/` | les magasins d'état, les schémas, la logique métier |
| `lib/` | les utilitaires dont cette slice a besoin |
| `config/` | les constantes, les drapeaux de fonctionnalité |

### La règle d'import, et l'API publique

Deux règles font le vrai travail.

**1. Un module ne peut importer que depuis des couches strictement inférieures à la sienne.** `pages/` peut employer `features/` ; `features/` ne peut jamais employer `pages/`. Les cycles deviennent structurellement impossibles.

**2. Une slice ne peut pas importer une slice sœur de sa propre couche.** `features/add-to-cart/` ne peut pas atteindre `features/checkout/`. Si deux features ont besoin de la même chose, cette chose appartient une couche plus bas — généralement dans `entities/` ou `shared/`.

Chaque slice expose une **API publique** à travers un `index.ts` à sa racine, et c'est le seul point d'entrée légal. Atteindre au-delà, jusque dans `features/checkout/ui/Button.tsx`, est une violation même depuis une couche qui aurait par ailleurs le droit de l'importer. L'API publique est ce qui vous permet de réorganiser l'intérieur d'une slice sans toucher à rien d'autre.

### Application contrainte

```bash
npm i -D steiger @feature-sliced/steiger-plugin
```

Configurez **`steiger.config.js`** et exécutez-le en intégration continue. Les règles qui comptent : `fsd/forbidden-imports` (imports vers le haut et imports entre slices), `fsd/no-public-api-sidestep` (atteindre au-delà d'un `index.ts`), `fsd/no-layer-public-api`.

**`.js`, et non `.ts`, et ce n'est pas une préférence de style.** Steiger charge une configuration TypeScript via cosmiconfig, qui appelle `typescript.findConfigFile` — retiré dans TypeScript 6. Avec TypeScript 6 installé, `steiger.config.ts` plante avant qu'une seule règle ne s'exécute. Une configuration `.js` n'a besoin d'aucun chargeur et fonctionne sous l'une comme sous l'autre version.

**Regardez chaque règle échouer avant de la croire.** Ajoutez un import depuis une couche supérieure, exécutez, voyez l'erreur, puis retirez l'import. Un garde-fou que personne n'a vu échouer est une affirmation plutôt qu'une garantie, et un linter silencieusement mal configuré est indistinguable d'une base de code sans violation.

### La règle sur laquelle vous devrez prendre une décision

`fsd/insignificant-slice` signale une slice qu'une seule autre slice importe, et suggère de la fusionner vers le haut. **Sa justification vaut d'être lue même si vous finissez par la désactiver :** *« chercher à tout décomposer en autant de couches et de slices que possible conduit la logique à s'étaler inutilement, ce qui annule le bénéfice de forte cohésion de Feature-Sliced Design. »*

**Sur une application à page unique, elle ne peut pas être satisfaite.** Un widget employé par la seule page que vous avez est référencé exactement une fois, par construction — la règle se déclenche donc sur chaque widget et chaque feature que vous écrirez jamais, et elle mesure votre nombre de pages plutôt que votre conception. Cela entre en collision frontale avec la référence des couches, qui dit qu'un widget est justifié quand *« la page à laquelle il appartient comporte plusieurs grands blocs indépendants »*.

**Deux morceaux de la recommandation d'une même méthodologie se contredisent, et vous devez choisir.** L'un comme l'autre est défendable ; ce qui ne l'est pas, c'est de choisir par accident, ou de laisser un contrôle rouge sur un arbre sain — un contrôle qui est rouge alors que rien ne va mal est ignoré en moins d'une semaine, et il n'applique alors plus rien tout en ayant l'air de le faire. **Décidez, et écrivez la raison là où la personne suivante la trouvera**, à côté de l'interrupteur plutôt que dans un message de commit. Notez aussi ce qui vous ferait revenir là-dessus : pour cette règle, une deuxième page.

**Une chose qui ne fonctionne pas, pour que vous n'y passiez pas un après-midi :** restreindre la règle à `widgets/` et `features/` par chemin. Le cadrage par chemin fait sortir ces fichiers du graphe de dépendances, après quoi vos entities paraissent référencées une seule fois et la règle invente des constats qui ne sont pas vrais.

C'est la réponse du frontend à `test_architecture.py`. Même travail, machine différente.

### En quoi ceci diffère du backend, dit franchement

**Les deux moitiés de ce kit n'emploient pas le même principe de structuration, et vous devriez le savoir plutôt que de le découvrir.**

| | backend | frontend (FSD) |
|---|---|---|
| Règle | imports à sens unique | imports à sens unique |
| Sens | **vers l'intérieur**, vers `entities/` — le code le plus abstrait et le plus stable | **vers le bas**, vers `shared/` — le code le plus réutilisable et le moins propre au métier |
| Organisé par | couche technique | slice métier, *puis* segment technique |
| Inversion de dépendance | disponible, et **la seule chose que la forme N-Layer de la partie 1 décline** — la partie 2 porte la question qui la décide | **non**, par conception ; les imports directs vers le bas sont permis |
| Appliqué par | un test pytest | un linter (Steiger) |

Les sens sont véritablement opposés : le backend pointe vers la politique métier, FSD pointe vers les utilitaires génériques. FSD a été décrit comme deux flux de développement pointant l'un vers l'autre — le backend construit de bas en haut depuis le domaine, le frontend construit de haut en bas depuis la page.

**Pourquoi c'est acceptable.** Les deux moitiés subissent des pressions différentes. La partie difficile d'un backend, ce sont des règles métier qui doivent rester correctes pendant que l'infrastructure change autour d'elles, et la règle de dépendance protège exactement cela. La partie difficile d'un frontend, c'est que les fonctionnalités se multiplient, que les équipes travaillent en parallèle, et que *« où va ce fichier »* est demandé vingt fois par jour. FSD répond directement à cette question, ce que la règle de dépendance ne fait pas.

**Ce que les deux partagent, et c'est la chose qui vaut d'être apprise :** chaque fichier a un ensemble déclaré de dossiers depuis lesquels il peut importer, cet ensemble est écrit, et une machine le vérifie. C'est l'idée transposable. Les noms de couches sont le dialecte local.

### La pile technique, et où vit chaque pièce

| Préoccupation | Choix | Vit dans |
|---|---|---|
| Routage | React Router | `app/` |
| État serveur | TanStack Query | le segment `api/` d'une slice ; les hooks de requête à côté des requêtes qu'ils enveloppent |
| État client | Zustand | le segment `model/` de la slice qui en est propriétaire |
| État d'interface local | `useState` | à l'intérieur du composant |
| Configuration et providers | React Context | `app/` |

**L'état serveur et l'état client sont deux choses différentes, et cette distinction est toute la raison pour laquelle il y a deux bibliothèques.**
Une donnée qui vit sur le serveur et qui est *mise en cache* dans le navigateur — une liste, un enregistrement, tout ce qui est récupéré — relève de TanStack Query : chargement, erreurs, nouvelles tentatives, invalidation et rechargement sont tous une seule préoccupation et elle est résolue. Une donnée qui n'existe jamais que dans le navigateur — l'état ouvert d'un panneau de filtres, un formulaire multi-étapes en cours, un élément sélectionné — relève de Zustand.

L'erreur de débutant la plus courante est de mettre une donnée serveur dans un magasin global et d'écrire l'invalidation de cache à la main. La deuxième plus courante est de recourir à un magasin global pour quelque chose dont un seul composant est propriétaire. Employez `useState` jusqu'à ce que deux composants sans rapport aient besoin de la même valeur.

**Context sert à la configuration, pas à un état qui change souvent.** Chaque consommateur se réaffiche à chaque changement, donc un thème ou un utilisateur courant convient, et une valeur mise à jour en direct ne convient pas.

### TypeScript

Le frontend est en TypeScript, et la raison est la frontière.

Le segment `api/` est l'endroit où existent les DTO serveur. Avec des types, « un DTO ne doit pas atteindre l'interface » cesse d'être une convention et devient une erreur de compilation : déclarez le type réseau dans `api/`, transformez-le vers votre propre type à la frontière, et n'exportez jamais le type réseau. C'est une garantie plus forte que n'importe quelle règle de chemin d'un linter — et c'est la même garantie que le backend obtient du fait qu'`entities/` n'a aucun import d'ORM.

Nommez les deux formes différemment et ne les laissez jamais fusionner : `UserDto` pour ce que le serveur a envoyé, `User` pour ce avec quoi votre application pense.

### Ce que `scaffold-frontend-app` pose

La compétence est à `.claude/skills/scaffold-frontend-app/`, et voici son travail :

1. `npm create vite@latest -- --template react-ts`, puis Tailwind.
2. Créer `src/{app,pages,widgets,features,entities,shared}`, avec `shared/{ui,api,lib,config}` et un `index.ts` dans chaque slice qu'elle crée.
3. Installer React Router, TanStack Query, Zustand ; câbler le routeur et le `QueryClientProvider` dans `app/`.
4. Installer et configurer `steiger` + `@feature-sliced/steiger-plugin`, et **prouver qu'il échoue sur un import vers le haut délibéré** avant de déclarer un succès — un linter que personne n'a vu passer au rouge est une affirmation, pas une garantie.
5. Mettre en place Vitest + Testing Library, avec des tests séparés entre `pure/` (pas de DOM, et un test qui importe React fait échouer un test) et `rendered/`.
6. Ne créer **aucune** feature, entity ni widget — ce sont du travail de user story, exactement comme la génération backend ne crée aucun `dal_*.py`. Elle ne crée même pas ces trois dossiers vides : Steiger produit des constats sur les slices vides et insignifiantes, donc les précréer vous remet un linter rouge sur un projet où vous n'avez rien écrit. **Une couche est créée par la première user story qui en a besoin.**
7. Vérifier que ça démarre, puis rapporter.

**Même précondition dure que la génération backend** : rien n'est généré avant que le périmètre ne soit convenu et que les documents n'existent.

---

## Partie 4 — Conventions de nommage

Énoncez-les dès l'instant où un langage entre dans votre projet, et étendez-les la première fois qu'une véritable erreur est attrapée — pas avant.

### Python

| Sorte | Convention | Exemple |
|---|---|---|
| Module | `snake_case`, préfixé par sa couche | `dal_user.py`, `bll_billing.py`, `ent_invoice.py` |
| Classe | `PascalCase`, portant le même préfixe | `DalUser`, `BllBilling`, `EntInvoice` |
| Ligne d'ORM privée | souligné en tête | `_UserRow` |
| Fonction, variable | `snake_case` | `find_by_email` |
| Constante | `UPPER_SNAKE_CASE` | `MAX_RETRIES` |
| Booléen | préfixé `is_` / `has_` / `can_` | `is_active`, `has_paid` |
| Dossier de paquet | minuscules, sans soulignés | `entities/`, `dal/`, `bll/` |

**Le préfixe de couche vaut sa laideur.** `dal_user.py` à côté de `bll_user.py` vous dit lequel est lequel dans un onglet de fichier, une trace d'appels, un résultat de recherche et une relecture de code — partout où un simple `user.py` ne le dirait pas. Le coût est réel et le gain est plus grand.

**Une règle dure vient avec :** un préfixe de couche ne doit jamais apparaître dans quoi que ce soit qu'un utilisateur lit sur un écran. C'est une aide de navigation interne, pas du vocabulaire.

### TypeScript / React

| Sorte | Convention | Exemple |
|---|---|---|
| Fichier de composant | `PascalCase.tsx`, nommé d'après son unique export | `UserCard.tsx` |
| Hook | `camelCase.ts`, préfixé `use` | `useCurrentUser.ts` |
| Module pur | `camelCase.ts` | `formatDate.ts` |
| Type ou interface | `PascalCase`, sans préfixe `I` | `User`, et non `IUser` |
| Type réseau | `PascalCase` + `Dto` | `UserDto` |
| Dossier (slice, segment) | `kebab-case` | `features/add-to-cart/` |
| Constante | `UPPER_SNAKE_CASE` | `PAGE_SIZE` |
| Booléen | `is` / `has` / `can` / `should` | `isLoading`, `canEdit` |
| Gestionnaire d'événement | `handleX` là où il est défini, `onX` comme propriété | `onSubmit={handleSubmit}` |
| API publique | `index.ts` à la racine de chaque slice | `features/add-to-cart/index.ts` |

Un composant par fichier, nommé comme son fichier. Un fichier qui exporte trois composants, ce sont trois fichiers qui n'ont pas encore été séparés.

### Horodatages, partout

**Stockez et transmettez en UTC. Toujours.** ISO-8601 avec `Z`. Convertissez en heure locale dans l'interface et nulle part ailleurs.
Cela vaut d'être énoncé le premier jour parce que le coût de l'erreur n'est pas un bogue que l'on corrige — ce sont des données stockées qui sont désormais ambiguës.

### Documents et dossiers

- `SCREAMING_SNAKE.md` pour les documents canoniques dont il existe exactement un : `PRD.md`, `PLAN.md`, `GLOSSARY.md`.
- `minuscules-avec-tirets.md` pour tout ce dont vous avez plusieurs exemplaires, et pour chaque dossier.
- **Les dossiers dont les fichiers forment un historique les numérotent `NN-nom.md`** — `reviews/`, `learnings/`. Le numéro est l'ordre dans lequel le fichier a été écrit, **attribué une fois et jamais réattribué**, parce qu'une citation dans un vieux commit doit continuer de se résoudre.
- Chaque fichier markdown ouvre sur `created` et `updated` en frontmatter YAML, en UTC, et `updated` est estampillé par `.githooks/pre-commit` plutôt que maintenu à la main.

### Étendre cette section

Ajoutez une ligne ici **la première fois qu'une véritable erreur de nommage est attrapée** — un composant nommé de façon incohérente, un horodatage stocké en heure locale, un booléen sans préfixe.
N'inventez pas de règles en avance sur le code qui en aurait besoin. Une liste de conventions écrite de façon spéculative est une liste que personne ne croit.

---

## Partie 5 — La pile technique recommandée

C'est ce que produisent les générateurs de structure du kit. **C'est un point de départ, pas une exigence.**

### Backend

| Pièce | Choix | Pourquoi celui-ci précisément |
|---|---|---|
| Langage | **Python 3.12+** | un typage désormais véritablement bon, et la plus grande surface de bibliothèques pour ce dont votre domaine aura besoin |
| Framework | **FastAPI** | asynchrone natif, documentation OpenAPI automatique issue de vos DTO, et validation Pydantic à la frontière, là où elle appartient |
| ORM | **SQLAlchemy 2.x**, déclaratif typé | de vraies colonnes et de vraies relations, pour que votre schéma soit un schéma plutôt qu'un bloc JSON |
| Migrations | **Alembic** | le schéma changera ; la seule question est de savoir si le changement est consigné. **Demandez d'abord : qui d'autre lit cette base de données, et pouvez-vous la supprimer ?** Seul, face à un fichier jetable, `create_all` est une indirection de moins — en ajout seulement, et vous l'assumez en le sachant |
| Base de données | **SQLite** pour commencer, **PostgreSQL** quand vous avez besoin d'écrivains concurrents | SQLite, c'est zéro configuration et un seul fichier ; c'est la DAL qui rend l'échange bon marché |
| Dépendances | **`uv`** | un seul fichier de verrouillage, assez rapide pour s'exécuter à chaque démarrage, installe votre paquet en mode éditable pour que les imports fonctionnent partout |
| Validation | **Pydantic v2** | des DTO qui se valident eux-mêmes à la frontière |
| Tests | **pytest** | avec `pytest-asyncio` en mode automatique |

### Frontend

| Pièce | Choix | Pourquoi celui-ci précisément |
|---|---|---|
| Langage | **TypeScript** | c'est ce qui rend la frontière des DTO contraignante plutôt qu'aspirationnelle |
| Framework | **React 19** | le plus grand écosystème, et la documentation comme l'outillage de FSD le supposent |
| Construction | **Vite** | serveur de développement instantané, et ce que suppose chaque guide actuel |
| Style | **Tailwind CSS 4** | un vocabulaire de jetons plutôt qu'une bibliothèque de composants contre laquelle vous vous battrez |
| Routage | **React Router** | le choix par défaut ; le routage par fichiers est une décision de framework, pas de bibliothèque |
| État serveur | **TanStack Query** | mise en cache, nouvelles tentatives et invalidation sont un seul problème résolu, et le refaire à la main est l'erreur de frontend la plus répétée |
| État client | **Zustand** | petit, sans partis pris, aucune cérémonie de provider. Redux Toolkit seulement pour une grande équipe sur une grande application |
| Tests | **Vitest + Testing Library + jsdom** | même configuration que Vite, pas de seconde chaîne de construction |
| Linting d'architecture | **Steiger** | la règle, vérifiée |

### Ce que coûte un échange

- **Une autre base de données** — presque gratuit, si `dal/` est honnête. C'est le découpage qui se rembourse.
- **Un autre framework Python** — une réécriture d'`api/`, rien d'autre. Là encore, le découpage qui se rembourse.
- **Un autre framework frontend** — FSD est indépendant du framework ; les couches et la règle survivent. Les composants, non.
- **Abandonner TypeScript** — la frontière `api/` redevient une convention, appliquée seulement par le linter et par vous.
- **Abandonner les contrôles d'architecture** — gratuit aujourd'hui, et vous serez incapable de dire quand cela cesse d'être gratuit. C'est celui de cette liste qu'il ne faut pas prendre.

---

## Partie 6 — Où ceci se situe dans votre parcours

```
1. Copier le kit dans votre projet vide            (README.md § Installation)
2. Lancer le prompt de démarrage                   STARTER_PROMPT.md
       ↓  remplit, une section à la fois, avec vos réponses :
   PRD → NFR → SOLUTION_DESIGN → PLAN → GLOSSARY → PROJECT_WORKFLOW
3. Écrire AGENTS.md / CLAUDE.md                    (dérivés, en dernier)
4. Planifier le premier Epic et ses user stories   compétences : epic, user-story
5. Générer la structure du backend                 compétence : scaffold-backend-service
6. Générer la structure du frontend                compétence : scaffold-frontend-app
7. Construire, une user story à la fois
```

**Les étapes 5 et 6 viennent après l'étape 2, et cet ordonnancement est l'affirmation centrale du kit.**
Générer la structure d'abord, c'est choisir ses couches avant de connaître son domaine, et la couche que vous choisirez mal est celle que vous ne remarquerez pas pendant un mois.

Lisez `project-docs/learnings/03-backend-layered-architecture-template.md` pour le raisonnement long derrière la partie 1, et `project-docs/learnings/01-documentation-structure-template.md` pour savoir pourquoi les documents sont ordonnés ainsi.

---

## Partie 7 — Où lire davantage

**Tout ce qui suit a été ouvert et vérifié.** Commencez par le haut de chaque liste ; elles sont ordonnées, pas alphabétiques.

> **Ces sources sont en anglais.** C'est la langue dans laquelle cette littérature existe, et c'est aussi le vocabulaire employé par les noms de couches et les identifiants de ce kit — ce qui est précisément la raison pour laquelle ils n'ont pas été traduits.

### La Clean Architecture et la famille des architectures en couches — commencez ici

**1. [The Clean Architecture](https://blog.cleancoder.com/uncle-bob/2012/08/13/the-clean-architecture.html)** — Robert C. Martin, ~10 min.
Le billet d'origine, et toujours l'énoncé complet le plus court. Si vous ne lisez qu'une chose, lisez celle-ci. C'est de là que vient la phrase sur la règle de dépendance de la partie 0, et c'est là que le diagramme en cercles concentriques que tout le monde redessine a été dessiné pour la première fois.

**2. [Common web application architectures](https://learn.microsoft.com/en-us/dotnet/architecture/modern-web-apps-azure/common-web-application-architectures)** — Microsoft Learn, ~20 min.
**La meilleure explication gratuite avec de vrais diagrammes**, et celle qui fera tout comprendre de la partie 1. Lisez *« What are layers »*, *« Traditional N-Layer architecture »* et *« Clean architecture »*, et arrêtez-vous à *« Monolithic applications and containers »* — le reste est de l'Azure et du Docker dont vous n'avez pas besoin.

C'est écrit en C#, et cela n'a aucune importance : la section qui enseigne le plus est celle qui explique pourquoi le N-Layer traditionnel place votre logique métier au-dessus de votre base de données, et comment inverser une seule dépendance corrige cela. Cet argument est indépendant du langage, et leur `UI / BLL / DAL` est exactement votre `api / bll / dal`. **Lisez-le en regard du premier tableau de la partie 2** : Microsoft présente l'inversion de cette dépendance comme le correctif, et la partie 2 vous pose la question qui décide si c'en est un pour vous.

**3. [The Onion Architecture](https://jeffreypalermo.com/2008/07/the-onion-architecture-part-1/)** — Jeffrey Palermo, ~8 min.
Lisez celui-ci pour la *raison*, que la partie 2 emprunte : la technologie d'accès aux données change tous les quelques années, elle ne doit donc pas être la chose sur laquelle tout le reste est bâti. Court, et l'argument est le plus clair des trois.

**4. [Hexagonal Architecture](https://alistair.cockburn.us/hexagonal-architecture/)** — Alistair Cockburn, ~15 min.
Le plus ancien des quatre noms et le plus citable. Vaut d'être lu une fois pour une seule idée : *« l'asymétrie à exploiter n'est pas celle entre les côtés gauche et droit de l'application, mais celle entre l'intérieur et l'extérieur. »* Dès que l'interface utilisateur et la base de données vous paraissent être la même sorte de chose, le reste de ce document devient évident.

### Quand vous voudrez aller plus loin

**[Anemic Domain Model](https://martinfowler.com/bliki/AnemicDomainModel.html)** — Martin Fowler, ~6 min.
L'objection à laquelle répond la partie 2. Lisez-la pour pouvoir décider délibérément, plutôt que de vous faire dire plus tard que vous avez construit un anti-motif.

**[Explicit Architecture: how I put it all together](https://herbertograca.com/2017/11/16/explicit-architecture-01-ddd-hexagonal-onion-clean-cqrs-how-i-put-it-all-together/)** — Herberto Graça, ~17 min. **Avancé.**
Le meilleur texte existant sur la façon dont Hexagonal, Onion et Clean se rapportent l'une à l'autre. **Une mise en garde, puisque c'est exactement la confusion contre laquelle la partie 2 prévient** : il y intègre le DDD et le CQRS à leurs côtés, ce qui est légitime pour son propos et n'est *pas* ce que vous construisez. Lisez-le pour les relations entre les styles d'architecture ; traitez le matériel sur le DDD et le CQRS comme une lecture complémentaire sur autre chose.

*Des livres, si vous en voulez :* Clean Architecture *de Martin (2017) est la version longue du lien 1.* Domain-Driven Design *d'Evans (2003) est un sujet différent — lisez-le quand votre domaine est véritablement difficile, et non pour comprendre cette disposition.*

### Feature-Sliced Design — le frontend

**1. [Overview](https://feature-sliced.design/docs/get-started/overview)** — ~10 min. Couches, slices, segments et la règle d'import. Toute la méthodologie en une page.

**2. [Tutorial](https://feature-sliced.design/docs/get-started/tutorial)** — un parcours pratique construisant un clone de Medium, en deux moitiés : décider la structure *sur papier* d'abord, puis l'écrire. Suppose React et TypeScript. **La moitié sur papier est celle qui a de la valeur** — décider à quelle couche quelque chose appartient avant de l'écrire est la compétence réelle.

**3. [Public API](https://feature-sliced.design/docs/reference/public-api)** — ~5 min. La convention de l'`index.ts`, et pourquoi atteindre au-delà est une violation même depuis une couche autorisée à vous importer.

**4. [Steiger](https://github.com/feature-sliced/steiger)** — le linter. Installez-le le premier jour, pas après que la structure a déjà dérivé.

### Des alternatives dont il vaut de savoir qu'elles existent

**[Bulletproof React](https://github.com/alan2207/bulletproof-react/blob/master/docs/project-structure.md)** — la principale alternative à FSD, fondée sur les fonctionnalités : moins de concepts, moins de cérémonie, une règle plus souple. Lisez sa section sur `import/no-restricted-paths` d'ESLint même si vous employez FSD — c'est l'exemple court le plus clair d'une frontière contrainte par l'outillage JavaScript.

### La documentation de la pile elle-même

[FastAPI](https://fastapi.tiangolo.com/tutorial/bigger-applications/) (*Bigger Applications* est la structure de routage que vous voulez) · [SQLAlchemy 2.0 ORM](https://docs.sqlalchemy.org/en/20/orm/quickstart.html) · [Alembic](https://alembic.sqlalchemy.org/en/latest/tutorial.html) · [uv](https://docs.astral.sh/uv/) · [Pydantic](https://docs.pydantic.dev/latest/) · [Vite](https://vite.dev/guide/) · [TanStack Query](https://tanstack.com/query/latest/docs/framework/react/overview) · [Zustand](https://zustand.docs.pmnd.rs/) · [React Router](https://reactrouter.com/) · [Tailwind](https://tailwindcss.com/docs) · [Vitest](https://vitest.dev/) · [Testing Library](https://testing-library.com/docs/react-testing-library/intro/)

---

*Si un lien ci-dessus est mort quand vous lisez ceci, les termes de recherche qui trouveront son remplaçant sont : « clean architecture dependency rule », « onion architecture Palermo », « hexagonal architecture ports adapters », « feature-sliced design layers ».*
