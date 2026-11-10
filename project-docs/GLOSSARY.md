---
created: 2026-11-09T00:00:00Z
updated: 2026-11-10T17:08:18Z
---

# GLOSSARY.md — CFDC

**Répond à :** que veut dire ce terme ? — à consulter dès qu'un mot est ambigu, une fois rempli.
**Dépend de :** rien pour la section « Workstream, Epic et Milestone » (générique, déjà présente) ; de `PRD.md`, et surtout de `PLAN.md`, pour tout le reste.

> **Statut : structure de départ — le dernier document à finaliser, pas le premier.** Contre-intuitivement, ce n'est pas par là qu'on commence : sans savoir encore quel produit c'est, vous ne savez pas quel vocabulaire mérite une entrée. Le véritable ordre : `PRD.md` → `NFR.md` → `SOLUTION_DESIGN.md` → `PLAN.md` → **ici, en dernier**. Ce fichier peut commencer à se remplir dès qu'un premier brouillon de PRD existe (les premiers termes émergent), mais il ne se **finalise** qu'une fois `PLAN.md` terminé — c'est là qu'il y a assez de matière pour savoir vraiment quel produit c'est. Chaque section porte les questions de réflexion à se poser avant d'écrire — ne demandez pas à l'agent d'inventer les réponses.

---

## Acteurs et rôles

| Terme | Définition |
|---|---|
| **Secrétaire** | Rôle qui saisit les informations : formations, sessions, participants, présences, notes. Plusieurs personnes peuvent l'avoir |
| **Coordonnateur** | Rôle qui valide les demandes de formation, planifie les sessions, voit tout, y compris les données personnelles des participants, et peut créer des comptes |
| **Chef de service du CFDC** | Rôle qui suit les formations, supervise cours et formateurs et organise les horaires. **Toujours un chef de service du CFDC** : le chef du service qui demande une formation n'a pas accès à l'application |
| **Formateur** | Rôle limité : il voit ses modules, leurs documents de cours et les noms de ses participants |
| **Administrateur informatique** | La « sentinelle » : crée, désactive et débloque les comptes, change les rôles, dépose les documents de cours, valide les demandes de correction, fait les sauvegardes |
| **Direction du CFDC** | Rôle qui consulte tout, sauf les données personnelles des participants. C'est la « personne autorisée » des premiers échanges |
| **Participant** | Personne qui suit une formation. **N'est pas un utilisateur** : il n'a pas de compte et la secrétaire l'enregistre |
| **Participant interne / externe** | Interne : agent de l'AAN. Externe : personne d'une entreprise extérieure, par exemple un concessionnaire |
| **Service demandeur** | Service de l'AAN (ou entreprise) qui adresse une demande de formation à la coordination et fournit la liste de ses participants. Il n'a pas accès à l'application |
| **Utilisateur** | Membre du personnel du CFDC qui a un compte. Une même personne peut avoir **plusieurs rôles** |

> **Questions à se poser :**
> 1. Qui ou quoi touche ce système, et chacun a-t-il besoin de capacités, d'accès ou de niveaux de confiance différents ?
> 2. Y a-t-il un mot (comme « utilisateur » ou « agent ») qui pourrait désigner deux choses différentes selon le contexte, ici ? Faut-il le scinder en deux termes ?
> 3. Y a-t-il des modes ou des intentions distincts dans lesquels un même acteur peut se trouver, et qui méritent d'être nommés séparément ?

---

## Composants du système

| Terme | Définition |
|---|---|
| **`frontend`** | L'interface React que le personnel ouvre dans son navigateur |
| **`backend`** | L'API FastAPI : sessions de connexion, droits, règles, journal, exports, envoi des codes |
| **Serveur de test / de production** | Les deux installations Docker Compose sur les serveurs de l'AAN : la première pour essayer, la seconde en service |
| **Double authentification (2FA)** | Le code à usage unique, valable 5 minutes, envoyé par email (par défaut) ou par SMS après le mot de passe |
| **Session de connexion** | La preuve, gardée par le serveur, qu'un utilisateur s'est connecté ; elle expire après 15 minutes d'inactivité. **À ne pas confondre avec une session de formation** |

> **Questions à se poser :**
> 1. Quelles sont les pièces exécutables ou déployables indépendamment de ce système ?
> 2. Deux composants portent-ils des noms assez proches pour être confondus ? Qu'est-ce qui distingue chacun en une phrase ?
> 3. Y a-t-il un découpage naturel qui mérite d'être nommé comme catégorie (public contre privé, permanent contre à la demande) ?

---

## Magasins de données

| Terme | Définition |
|---|---|
| **Base de données** | PostgreSQL, la seule source de vérité |
| **Dossier des documents** | Le volume disque où sont stockés les fichiers des documents de cours |
| **Journal** | La trace de chaque modification et suppression : qui, quoi, quand, avant, après. Rien n'y est jamais effacé |

> **Questions à se poser :**
> 1. Où l'information persiste-t-elle réellement, et combien de magasins distincts y a-t-il ?
> 2. Un magasin détient-il plus d'une sorte de donnée qui mériterait d'être nommée séparément ?
> 3. Quel magasin, s'il était perdu, causerait le plus de dommages ?

---

## Vocabulaire du domaine

| Terme | Définition |
|---|---|
| **AAN** | Autorité Aéroportuaire Nationale |
| **CFDC** | Centre de Formation et de Développement des Compétences de l'AAN, rattaché à la direction des ressources humaines |
| **Formation** | Un programme du catalogue, par exemple « conduite sur le tarmac ». Elle a un domaine et contient plusieurs modules. Elle peut être donnée plusieurs fois par an |
| **Domaine** | La catégorie d'une formation, par exemple sûreté ou sécurité. Liste fixe, à fournir |
| **Module** | Un cours d'une formation, dispensé par **un seul** formateur, avec ses documents de cours |
| **Session** (de formation) | Une occurrence datée d'une formation, d'une heure à une semaine |
| **Formation importante** | Formation que le coordonnateur décide de marquer ainsi ; ses participants reçoivent un certificat |
| **Demande de formation** | La requête administrative écrite d'un service demandeur, validée par le coordonnateur puis enregistrée |
| **Inscription** | La présence d'un participant dans une session, avec sa présence, sa note et la remise de ses documents |
| **Présence** | Un seul « présent / absent » par participant et par session, même sur plusieurs jours |
| **Évaluation** | Une note sur 100 et des commentaires, une par participant et par session. Réussite à partir de 50/100 |
| **Attestation** | Preuve de participation, remise à tous les participants présents. Produite **hors de l'application**, qui note sa remise et sa date |
| **Certificat** | Document remis en plus de l'attestation, sur demande ou pour une formation importante. Produit hors de l'application |
| **Demande de correction** | Demande, faite dans l'application, de modifier ou de supprimer une information déjà enregistrée. Seul l'administrateur la valide. **À ne pas confondre avec une demande de formation** |
| **Données personnelles** | Le NIF, le CIN et le téléphone d'un participant. Visibles seulement du coordonnateur et de l'administrateur après saisie |
| **NIF / CIN** | Numéro d'identification fiscale / carte d'identification nationale. Au moins l'un des deux est obligatoire ; il sert à reconnaître une même personne d'une session à l'autre |
| **Badge AAN** | Le numéro de badge du personnel, au format `A00-00`, qui sert d'identifiant de connexion |

> **Questions à se poser :**
> 1. Quels noms récurrents ou noms de processus une personne extérieure interpréterait-elle de travers sans définition ?
> 2. Quels termes reviennent sans arrêt dans les conversations sur ce projet sans être évidents à partir du mot seul ?
> 3. Y a-t-il un terme emprunté à un champ plus large qui signifie ici quelque chose de plus étroit ?

---

## Workstream, Epic et Milestone

*Générique — à réutiliser tel quel.*

- **Workstream** = *quel domaine fonctionnel*. Ne se termine jamais. Peut être revisité par un Epic ultérieur. Identifiant : `WS-NN` (deux chiffres).
- **Epic** = *quand, et quelle quantité à la fois*. Étape de construction séquentielle et bornée dans le temps. Identifiant : `epic-NNN-name` (dossier à trois chiffres).
- **Milestone** = *ce qui est livré*. La représentation GitHub d'un Epic — et non un quatrième concept distinct.

> **Question à se poser :** ce projet a-t-il véritablement besoin des trois axes, ou est-il assez petit pour que deux d'entre eux se confondent en un seul ? Quels sont les Workstreams réels de ce projet, indépendamment de l'ordre dans lequel ils seront construits ?

**Dans CFDC :** les six Workstreams (`WS-01` à `WS-06`) sont définis dans `SOLUTION_DESIGN.md` §2, les six Epics dans `PLAN.md`. Chaque Epic devient un Milestone sur le tableau GitHub « CFDC » n° 4.

---

## Documents du projet

*Générique — simple renvoi.*

Le document canonique listant tous les autres documents du projet : voir `PRD.md` § Documents liés.

---
