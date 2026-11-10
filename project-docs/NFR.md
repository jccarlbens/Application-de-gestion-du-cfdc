---
created: 2026-11-09T00:00:00Z
updated: 2026-11-10T16:38:55Z
---

# NFR.md — CFDC

**Répond à :** quel niveau de qualité ce produit doit-il atteindre ?
**Dépend de :** `PRD.md` (document compagnon, et non un sous-ensemble de celui-ci).

> **Statut : structure de départ.** Modèle ISO 25010, générique — il y a peu à généraliser ici, mais chaque question mérite quand même une vraie réponse pour CE projet, et non une réponse générique qui conviendrait à n'importe quel projet.
>
> **Note sur le sigle.** `NFR` veut dire *Non-Functional Requirements* — les exigences non fonctionnelles. Le nom du fichier reste en anglais, comme tous les chemins de ce kit.

---

## Performance

> 1. Quel temps de réponse donnerait à un utilisateur réel l'impression que c'est cassé ?
> 2. Y a-t-il un moment de charge de pointe connu ?
> 3. Que mesure-t-on réellement — le temps de chargement d'une page, la latence d'une API, autre chose ?

- **Seuil de l'inacceptable :** ouvrir une page ou enregistrer une saisie ne prend **jamais plus de 5 secondes**.
- **Recherche :** l'historique et les informations d'une formation se retrouvent en **2 minutes au plus**, gestes de l'utilisateur compris (`PRD.md` §11).
- **Pointes de charge :** elles dépendent des demandes de formation, par exemple une formation importante avec beaucoup de participants à saisir d'un coup.
- **Utilisateurs simultanés :** **10** au maximum.

## Fiabilité et disponibilité

> 1. Que signifie « en panne » pour ce produit, précisément ?
> 2. Une indisponibilité est-elle acceptable, et quand ?
> 3. Quel est le plan si une dépendance dont ceci dépend tombe ?

- **Disponibilité :** l'application est accessible **24 h/24, 7 j/7**.
- **Panne tolérée :** au plus **une heure** avant que ce soit grave. Une application hors service est un motif de retrait (`PRD.md` §12).
- **Coupure d'internet :** pouvoir continuer à saisir **hors ligne**, puis envoyer les saisies au retour de la connexion, serait intéressant, mais c'est une **amélioration ultérieure**, hors de la V1.
- **Si l'envoi des codes de double authentification tombe :**
  - l'utilisateur **bascule sur l'autre canal** (SMS si l'email ne passe pas, et inversement) ;
  - en dernier recours, l'**administrateur informatique** peut lui donner un **code de secours**.

## Capacité de montée en charge

> 1. Que se passe-t-il si l'usage est multiplié par dix du jour au lendemain ?
> 2. Quelle ressource s'épuise la première ?
> 3. La montée en charge est-elle ici un risque réel à court terme, ou une hypothèse pour la V1 ?

**Pas de montée en charge prévue.** L'application sert le personnel du CFDC, une dizaine de personnes, et aucune extension à d'autres directions ou aéroports de l'AAN n'est envisagée. La montée en charge n'est pas un risque pour la V1.

## Sécurité

> 1. Quelle est la chose la plus sensible que ce système détient ?
> 2. Qui ne doit jamais pouvoir y accéder ?
> 3. Quel est le pire scénario de compromission, et est-il survivable ?

**Ce que le système détient de plus sensible :** les données personnelles des participants (NIF, CIN, téléphone) et leurs évaluations.

**Qui ne doit jamais y accéder :** toute personne extérieure au CFDC, y compris un chef de service d'un autre service de l'AAN. Au sein du CFDC, les données personnelles ne sont visibles que du coordonnateur et de l'administrateur informatique, une fois saisies (`PRD.md` §7).

**Le pire scénario :** une fuite de données personnelles. C'est un motif de retrait de l'application (`PRD.md` §12).

**Les mesures :**
- **Connexion** par numéro de badge AAN, mot de passe et double authentification (email ou SMS).
- **Mot de passe :** au moins **8 caractères**, dont au moins un chiffre ; **aucun changement obligatoire** à intervalle fixe.
- **Blocage :** après **5 échecs** de connexion, le compte est bloqué ; seul l'**administrateur informatique** le débloque.
- **Déconnexion automatique** après 15 minutes d'inactivité.
- **Traçabilité :** chaque modification et chaque suppression garde qui, quoi et quand.
- **Hébergement :** sur les **serveurs de l'AAN**, gérés par le **service informatique de l'AAN**.

## Utilisabilité et accessibilité

> 1. Qui pourrait avoir du mal à utiliser ceci tel que conçu — appareil, langue, capacités ?
> 2. Y a-t-il une norme d'accessibilité minimale visée ?
> 3. Quelle est la tâche la plus simple qu'un utilisateur novice doit pouvoir accomplir sans aide ?

**La simplicité d'utilisation est l'exigence première** (`PRD.md` §2 et §4) : une interface difficile ferait revenir le personnel au papier, et c'est un motif de retrait (`PRD.md` §12).

- **Langue :** l'interface est en **français** seulement.
- **Prise en main :** une **formation** des utilisateurs suffit ; pas d'aide à l'écran ni de guide exigés. Cette formation est une condition de mise en service (`PRD.md` §12).
- **Test du novice :** un nouvel utilisateur sait **inscrire un participant à une session** sans aide.
- **Norme d'accessibilité :** *(à préciser)*

## Compatibilité

> 1. Sur quels environnements (navigateurs, appareils, systèmes d'exploitation) ceci doit-il réellement fonctionner ?
> 2. Y a-t-il un environnement explicitement non pris en charge ?
> 3. Faut-il interopérer avec un système existant ?

- **Appareils :** les **ordinateurs Windows** du CFDC, des postes **pas très récents**. L'application est un site web, utilisable aussi sur téléphone (`PRD.md` §13), mais l'ordinateur est l'usage principal.
- **Navigateurs :** *(à préciser)*
- **Interopérabilité :** aucune. L'application n'est reliée à aucun autre système de l'AAN (`PRD.md` §13).

## Conformité et aspects juridiques

> 1. Quelle réglementation s'applique à ces données ou à ce public ?
> 2. Quel consentement ou quelle information est légalement exigé avant de collecter des données ?
> 3. Qui est responsable si cela tourne mal ?

*(À écrire)*

## Maintenabilité

> 1. À quel point est-il facile, pour une personne future — y compris vous-même plus tard — de modifier ceci sans danger ?
> 2. Quel est le plan pour maintenir la documentation en phase avec le code ?
> 3. Y a-t-il une suite de tests, et que couvre-t-elle réellement ?

*(À écrire)*

## Portabilité

> 1. Ceci pourrait-il déménager chez un autre hébergeur sans réécriture complète ?
> 2. Y a-t-il quelque chose de codé en dur pour un fournisseur unique qui ne devrait pas l'être ?

*(À écrire)*

## Observabilité et supervision

> 1. De quoi voudriez-vous être alerté immédiatement en cas de panne ?
> 2. Qu'est-ce qui est journalisé aujourd'hui, par rapport à ce qui devrait l'être ?
> 3. Qui surveille cela réellement ?

*(À écrire)*

## Reprise après sinistre et sauvegardes

> 1. Quel est le pire scénario de perte de données, et comment vous en remettriez-vous ?
> 2. À quelle fréquence les données sont-elles sauvegardées, et une restauration a-t-elle déjà été réellement testée ?
> 3. Quelle perte de données (RPO) et quelle indisponibilité (RTO) sont acceptables ?

*(À écrire)*

## Risques et mesures d'atténuation

> 1. Qu'est-ce qui risque le plus de mal tourner avant la livraison ?
> 2. Pour chaque risque, quel est le plan s'il se produit malgré tout ?
> 3. De quel risque, s'il se produisait, serait-il le plus difficile de se relever ?

*(À écrire)*

## Dépendances

> 1. De quels services externes, bibliothèques ou personnes ceci dépend-il pour fonctionner ?
> 2. Que se passe-t-il si l'un devient indisponible ou change son API ?
> 3. Y a-t-il parmi eux un point de défaillance unique ?

*(À écrire)*

---
