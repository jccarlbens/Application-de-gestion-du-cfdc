---
created: 2026-11-09T00:00:00Z
updated: 2026-11-24T17:18:13Z
---

# SOLUTION_DESIGN.md — CFDC

**Répond à :** comment est-ce construit ? En quels Workstreams cela se décompose-t-il ?
**Dépend de :** `PRD.md` + `NFR.md`.

> **Statut : structure de départ.** Les sections marquées **Conditionnelle** sont des suppositions quant à leur pertinence — confirmez-les explicitement.

---

## 1. Objet et périmètre

> 1. De quoi ce document est-il responsable de décider, qu'aucun autre document ne décide ?
> 2. Qu'est-ce qui est explicitement en dehors de l'autorité de ce document (par exemple, les décisions produit appartiennent au PRD) ?

**Ce document décide** comment l'application CFDC est construite : ses Workstreams, ses composants, sa pile technique, son modèle de données, son authentification, son déploiement, et les décisions d'architecture (ADR) qui les justifient.

**Il ne décide pas :**
- **ce que fait le produit, pour qui, et ce qui est hors périmètre** : c'est `PRD.md` ;
- **le niveau de qualité attendu** (performance, sécurité, sauvegardes…) : c'est `NFR.md`, que ce document doit respecter ;
- **l'ordre de construction** : c'est `PLAN.md`.

## 2. Workstreams — définition canonique de `WS-NN`

> **Rappel de vocabulaire (générique, indépendant du produit — voir aussi `GLOSSARY.md` § Workstream, Epic et Milestone) :**
> - **Workstream** = *quel domaine fonctionnel*. Ne se termine jamais, peut être revisité par un Epic ultérieur. Identifiant : `WS-NN` (deux chiffres).
> - **Epic** = *quand, et quelle quantité à la fois*. Étape de construction séquentielle et bornée dans le temps. Identifiant : `epic-NNN-name`.
> - **Milestone** = *ce qui est livré*. La représentation native GitHub d'un Epic, et non un concept distinct.
>
> Les Workstreams se définissent ici ; les Epics (qui regroupent des Workstreams dans le temps) se définissent ensuite, dans `PLAN.md`.

> 1. Quels sont les domaines fonctionnels indépendants de ce système, indépendamment de l'ordre de construction ?
> 2. Deux Workstreams pourraient-ils être travaillés par des personnes différentes en même temps sans se gêner ?
> 3. Y a-t-il un Workstream caché à l'intérieur d'un autre qui mériterait son propre identifiant ?

| Id | Workstream | Contenu | Capacités du PRD |
|---|---|---|---|
| WS-01 | Comptes et accès | Connexion par badge, double authentification, rôles, blocage après 5 échecs, déconnexion automatique, création et désactivation des comptes, mot de passe oublié | `PRD.md` §6 « Accès », §9 |
| WS-02 | Formations et modules | Catalogue des formations, modules, formateurs, documents de cours | §6 « Formations, modules et documents » |
| WS-03 | Demandes et planification | Demandes de formation, sessions, horaires | §6 « Demandes et planification » |
| WS-04 | Participants et suivi | Participants, inscriptions, présences, évaluations, remise des attestations et des certificats | §6 « Participants, présences et évaluations » |
| WS-05 | Corrections et traçabilité | Demandes de correction, validation par l'administrateur, historique des modifications, journal | §6 « Corrections », §7 |
| WS-06 | Consultation | Vue d'ensemble de l'unité, recherche, export Excel et PDF | §6 « Consultation », §10 |

*Validé par l'utilisateur le 2026-11-10.*

## 3. Vue d'ensemble du système

> 1. En quelques phrases, comment les pièces principales s'articulent-elles de bout en bout ?
> 2. Quel est le diagramme ou le flux unique qui expliquerait cela le plus vite à un nouvel ingénieur ?

Le personnel du CFDC ouvre l'application dans son navigateur, sur le **réseau interne de l'AAN**. L'interface React appelle l'API FastAPI, qui vérifie la session et les droits, puis lit ou écrit dans PostgreSQL et, pour les documents de cours, sur le disque. Pour la double authentification et le mot de passe oublié, l'API envoie des emails (SMTP) et des SMS (Digicel, Natcom).

```text
Navigateur (Chrome / Edge, réseau interne AAN)
        │  HTTPS
        ▼
   frontend  ── interface React, fichiers statiques
        │  /api
        ▼
   backend   ── API FastAPI : session, droits, règles métier, journal
     │      │                         │
     ▼      ▼                         ▼
 PostgreSQL  dossier des documents   SMTP (emails) · Digicel / Natcom (SMS)
```

## 4. Carte des composants

> 1. Quels sont les composants réellement exécutables ou déployables, et qu'est-ce que chacun possède ?
> 2. Quels ports, quelles URL, quels points d'entrée chacun expose-t-il ?
> 3. Y a-t-il ici un composant qui est en réalité deux composants déguisés en un seul ?

| Composant | Ce qu'il possède | Point d'entrée |
|---|---|---|
| `frontend` | L'interface React, servie en fichiers statiques | `https://<serveur>/` |
| `backend` | L'API FastAPI : sessions, droits, règles métier, journal, exports, envoi des codes | `https://<serveur>/api/v1/` |
| `db` | La base PostgreSQL, source de vérité | interne aux conteneurs, jamais exposée |
| volume `documents` | Les fichiers des documents de cours | lu et écrit par `backend` seulement |

Les quatre tournent ensemble dans un même Docker Compose (ADR 3). Les adresses exactes dépendent des serveurs de l'AAN (§15, Q1).

## 5. Pile technique

> 1. Quelle est la pile pour chaque partie majeure du système, et pourquoi ce choix précisément ?
> 2. Y a-t-il une pièce de la pile qui est un espace réservé ou une supposition plutôt qu'une vraie décision à ce stade ?

La pile reprend celle de `fds-pay` et la recommandation de `_ARCHITECTURE_EXPLAINED.md` partie 5, avec quatre ajouts (ADR 1 à 4).

**Backend**

| Pièce | Choix |
|---|---|
| Langage, framework | **Python 3.12+**, **FastAPI**, architecture en couches `entities / dal / bll / api` |
| Base de données | **PostgreSQL**, dès le départ (ADR 2) |
| ORM, migrations | **SQLAlchemy 2.x**, **Alembic** |
| Validation | **Pydantic v2** |
| Export | **openpyxl** (Excel), **fpdf2** (PDF) |
| Emails | **SMTP**, serveur configurable (double authentification, mot de passe oublié) |
| SMS | un **adaptateur par opérateur**, **Digicel** et **Natcom**, derrière une même interface (ADR 4) |
| Documents de cours | fichiers stockés sur le **disque du serveur**, dans un dossier sauvegardé avec la base (ADR 4) |
| Dépendances, tests | **uv**, **pytest** |

**Frontend**

| Pièce | Choix |
|---|---|
| Langage, framework | **TypeScript**, **React**, **Vite**, organisé en **Feature-Sliced Design** |
| Style | **Tailwind CSS** |
| Routage, état | **React Router**, **TanStack Query**, **Zustand** |
| Tests, architecture | **Vitest + Testing Library**, **Steiger** |

**Emballage et déploiement :** **Docker Compose** (ADR 3).

**Ce qui reste une supposition :** que le service informatique de l'AAN accepte Docker sur ses serveurs (§15, Q1).

## 6. Couche de données

> 1. Où vit réellement chaque sorte de donnée, et sous quelle forme ?
> 2. Quel magasin est la source de vérité si deux magasins pouvaient se contredire ?
> 3. Quel est le schéma ou le contrat, assez précisément pour que deux implémentations ne dérivent pas ?

**Où vivent les données.**
- **PostgreSQL** est la seule source de vérité pour toutes les fiches ci-dessous.
- **Dates et heures prévues** (date de réception d'une demande, dates et créneaux d'une session) : des dates et heures du **calendrier de l'AAN** (`LOCAL_TIMEZONE`, `America/Port-au-Prince`), gardées **sans fuseau**. Une session « de 8 h à 12 h » reste de 8 h à 12 h, quel que soit le fuseau du serveur. Les **traces** (journal, connexions, dépôts) restent des instants en UTC (affinage de l'Epic 3, E3-8).
- **Les documents de cours** sont des fichiers sur le disque du serveur ; la base ne garde que leur chemin et leurs métadonnées (ADR 4).

**Les fiches.** Leurs noms de tables et de champs seront en anglais, au pluriel, en `snake_case` ; le détail des colonnes s'écrira avec les migrations.

| Fiche | Contenu principal |
|---|---|
| **Utilisateur** (`users`, `user_roles`) | numéro de badge (une lettre majuscule, deux chiffres, un tiret, deux chiffres : `[A-Z]\d{2}-\d{2}`, unique), prénom et nom séparés, email (obligatoire, unique), téléphone (facultatif), rôles (un ou plusieurs, une ligne par rôle dans `user_roles`), canal de double authentification, actif ou désactivé, bloqué ou non, mot de passe haché en **Argon2id** (vide tant que la personne ne l'a pas choisi). Tables d'accès associées : `password_tokens` (liens de mot de passe, empreinte seulement), `login_attempts` (tentatives de connexion), `auth_sessions` (sessions de connexion). Détail : `technical-specs/ws-tech-01-accounts-and-access.md` |
| **Formation** (`trainings`) | intitulé (200 caractères au plus), `title_key` (l'intitulé sans majuscules ni espaces en trop, **unique**), description (facultative, 2 000 caractères au plus), sous-domaine. Journalisée (US-010) |
| **Domaine** et **sous-domaine** (`domains`, `subdomains`) | deux niveaux de classement : un domaine (nom unique) contient des sous-domaines (nom unique dans son domaine) ; une formation se range dans un sous-domaine. Journalisés ; la liste de départ est chargée par la migration `b88262b5a722`, donc hors du journal (US-010) |
| **Module** (`modules`) | formation, titre (200 caractères au plus, `title_key` **unique dans la formation**), description (facultative), formateur (un **utilisateur** ayant le rôle formateur, ou vide : « Formateur à désigner » ; les formateurs ont un compte limité à leurs modules, `PRD.md` §5), date d'ajout (`clock_timestamp()`, qui fixe l'ordre). Journalisé **sous sa formation** (US-011) |
| **Document de cours** (`course_documents`) | module, nom du fichier d'origine, type, taille, nom sur le disque (aléatoire, dans `DOCUMENTS_DIR`), déposé par, date, « remplacé par » (vide tant qu'il est en vigueur). PDF, Word, PowerPoint, 25 Mo au plus, contenu vérifié. Journalisé **sous sa formation** ; rien ne s'efface : remplacer ajoute une version (US-012) |
| **Demande de formation** (`training_requests`) | service demandeur (texte libre, 150 caractères), interne ou externe, date de réception, formation du catalogue, nombre de participants prévu (1 à 500), période souhaitée, commentaire ; statut **en attente → validée ou refusée** (décision définitive, corrigée par l'administrateur seul), avec qui a décidé, quand et le motif ; qui l'a enregistrée. Journalisée ; ajustable par la secrétaire et le coordonnateur, exception voulue (`PRD.md` §2) (US-014) |
| **Session** | formation, demande d'origine (facultative), date de début, date de fin, horaires. Une session dure **d'une heure à une semaine** |
| **Participant** | nom, prénom, **NIF ou CIN** (au moins l'un des deux, obligatoire ; il sert à reconnaître la même personne d'une session à l'autre), fonction, service ou entreprise, téléphone, interne ou externe |
| **Inscription** (un participant dans une session) | inscrit par, présence (**un seul** présent ou absent pour toute la session, même si elle dure plusieurs jours), note sur 100, commentaires, date de remise de l'attestation, date de remise du certificat |
| **Demande de correction** | fiche visée, modification ou suppression, changement proposé, demandeur, décision de l'administrateur |
| **Journal** (`audit_log`) | heure, auteur (utilisateur ou libellé : « Ligne de commande (administrateur) », « Titulaire du compte (lien de mot de passe) »), fiche visée, table, action, valeurs avant et après en JSON. Écrit automatiquement dans la même transaction que la modification ; la base refuse de le modifier ou de le supprimer (ADR 6). Secrets jamais recopiés ; données personnelles masquées à la lecture (`PRD.md` §7) |

**Les listes de référence.**
- **Domaines et sous-domaines de formation** (donnés le 2026-11-19, tenus ensuite par l'administrateur) :
  - **Sûreté-Sécurité** : Sensibilisation sur la carte d'accès, Conduite sur la rampe, Formation des policiers ;
  - **Accueil** : Protocole, Civilité.
- **Services de l'AAN et entreprises externes :** une liste, que l'utilisateur fournira, avec une option « Autre ». En attendant, ils se saisissent en **texte libre**.

## 7. Flux d'authentification et d'autorisation *(Conditionnelle — à sauter s'il n'y a aucun contrôle d'accès)*

> 1. Étape par étape, comment passe-t-on d'anonyme à authentifié, puis à autorisé pour une action précise ?
> 2. Qu'est-ce qui est émis (un jeton, une session, une clé), et que prouve-t-il réellement ?

**De l'anonyme à l'autorisé, étape par étape :**
1. L'utilisateur saisit son **numéro de badge** et son **mot de passe**. Chaque tentative est notée dans `login_attempts`, sans le mot de passe. Après **5 échecs consécutifs**, le compte est bloqué jusqu'à ce que l'administrateur le débloque.
2. Le serveur envoie un **code de double authentification** par le canal choisi (email par défaut, ou SMS). Le code vaut **5 minutes** et ne sert **qu'une fois**. Si le canal échoue, le serveur bascule sur l'autre ; en dernier recours, l'administrateur donne un code de secours. **Pas encore construite :** aujourd'hui, la session s'ouvre directement après le mot de passe ; cette étape arrive avec l'Epic 7 (US-005, US-008), **avant la mise en service**.
3. Une fois le code vérifié, le serveur ouvre une **session côté serveur** (table `auth_sessions`, empreinte du jeton seulement ; cookie `cfdc_session`), dont l'identifiant est remis dans un **cookie protégé** (`HttpOnly`, `Secure`, `SameSite`) qu'aucun script du navigateur ne peut lire.
4. La session expire après **15 minutes sans activité** ; chaque action la prolonge.
5. **À chaque action**, le serveur vérifie que l'un des rôles de l'utilisateur l'autorise (`PRD.md` §5). L'interface masque ce qui n'est pas permis, mais c'est le serveur qui décide.

**Ce que prouve la session :** que cette personne a présenté son badge, son mot de passe et un code reçu sur son email ou son téléphone il y a moins de 15 minutes d'inactivité. Désactiver ou bloquer un compte ferme ses sessions **immédiatement** (ADR 5).

## 8. Architecture temps réel ou interactive *(Conditionnelle — à sauter si rien n'est en direct ni en flux)*

> 1. Qu'est-ce qui doit se passer en temps réel, par rapport à ce qui peut rester en requête/réponse ?
> 2. Quel est le repli si le canal temps réel tombe au milieu d'une interaction ?

**Non applicable.** Rien ne se met à jour en direct : tout fonctionne en requête et réponse.

## 9-10. Boucle de mise à jour ou de retour automatisée *(Conditionnelle — à sauter si le contenu et le comportement ne changent que par édition manuelle)*

> 1. Quelque chose dans ce système se met-il à jour tout seul en fonction de l'usage ou de nouvelles données ? Qu'est-ce qui le déclenche ?
> 2. Qui relit un changement automatisé avant sa mise en service, si quelqu'un le fait ?
> 3. Quelle est la pire chose qu'une boucle de mise à jour automatisée pourrait faire si on la laissait sans contrôle ?

**Non applicable.** Rien ne change tout seul : toutes les informations sont saisies à la main.

## 11. Vue d'ensemble du déploiement

> 1. Où ceci tourne-t-il réellement aujourd'hui, et où tournera-t-il au lancement ?
> 2. Quel est le chemin entre un changement local et sa mise en service ?
> 3. Y a-t-il une étape de CI/CD, et qu'est-ce qu'elle conditionne réellement ?

**Deux environnements**, chacun lancé par Docker Compose (ADR 3) :
- un serveur de **test**, où la secrétaire et les autres utilisateurs essaient les nouveautés ;
- un serveur de **production**, en service.

Tous deux sont prévus sur les serveurs de l'AAN. **En attendant leur accès, le serveur de test tourne sur Render** (interface et API, deux services Docker gratuits, `render.yaml`), **avec la base sur Neon**, et ne reçoit **que des données fictives** (`NFR.md` § Risques). Il se redéploie **automatiquement à chaque fusion sur `main`**. Les emails y partent par Brevo (SMTP) ; en local, par Mailpit.

**Du changement à la mise en service :**
1. Une branche, une **pull request** sur GitHub.
2. **GitHub Actions** exécute les tests du backend et du frontend, et le contrôle d'architecture ; la fusion sur `main` exige qu'ils passent.
3. Sur les serveurs de l'AAN, l'administrateur déploiera **à la main** (`docker compose`), puisqu'ils ne sont pas joignables depuis GitHub. Le serveur de test actuel, sur Render, se redéploie tout seul après la fusion.
4. Une fois l'essai validé, il déploie la même version en production.

## 12. Hypothèses

> 1. Qu'est-ce que cette conception suppose vrai sans que cela ait été réellement vérifié ?
> 2. Quelle hypothèse, si elle était fausse, imposerait une refonte plutôt qu'un correctif ?

*Confirmées par l'utilisateur le 2026-11-10, sauf mention contraire.*
1. Les serveurs de l'AAN sont **accessibles depuis les postes du CFDC**.
2. L'application reste **sur le réseau interne de l'AAN** : elle n'est pas joignable depuis internet. Un téléphone ne peut l'utiliser que connecté à ce réseau.
3. Les postes du CFDC ont **Chrome ou Edge à jour**, sous Windows 10.
4. Chaque membre du personnel du CFDC a une **adresse email**.
5. **Plusieurs personnes** peuvent avoir le rôle de secrétaire.
6. *Non vérifiée :* le serveur peut **sortir vers internet** pour envoyer les emails et les SMS, même si l'application n'est pas joignable de l'extérieur. Si c'est faux, la double authentification doit passer par un serveur d'email interne de l'AAN (§15, Q3).

**Celle qui imposerait une refonte :** la n° 2. Ouvrir l'application à internet changerait les exigences de sécurité.

## 13. Hors périmètre

> 1. Qu'est-ce qui est architecturalement exclu de cette version, et pourquoi ?
> 2. Y a-t-il ici une exclusion qu'un Workstream ultérieur devra revisiter ?

- **Le mode hors ligne** : exclu de la V1 (`PRD.md` §13). Le choix d'une interface React le rend possible plus tard. **À revisiter.**
- **Une application mobile** : exclue ; l'interface web s'adapte au téléphone.
- **Les échanges avec d'autres systèmes de l'AAN** (ressources humaines, badges) : aucune API d'échange n'est prévue.
- **Le temps réel** : tout fonctionne en requête et réponse (§8).
- **Un stockage de fichiers dans le nuage** : rejeté (ADR 4).
- **L'accès depuis internet** : l'application reste sur le réseau interne (§12).

## 14. Registres de décision d'architecture (ADR)

> **Questions à se poser, pour chaque nouvelle entrée :**
> 1. Qu'a-t-on décidé qui aurait plausiblement pu aller dans l'autre sens ?
> 2. Pourquoi l'autre option a-t-elle été rejetée, assez précisément pour que personne ne la repropose sans le savoir ?

### ADR 1 — Reprendre la pile de `fds-pay` (FastAPI + React)
*2026-11-10.* **Décidé :** FastAPI et React + TypeScript en Feature-Sliced Design. **Pourquoi :** l'auteur connaît déjà cette pile, les compétences `scaffold-backend-service` et `scaffold-frontend-app` du dépôt la génèrent, et une interface React facilitera le mode hors ligne prévu plus tard. **Rejeté :** **Django**, qui fournit d'origine un écran d'administration et l'authentification, avec moins de code ; rejeté parce qu'il ferait perdre les générateurs du dépôt et l'acquis de `fds-pay`.

### ADR 2 — PostgreSQL dès le départ
*2026-11-10.* **Décidé :** PostgreSQL, sans passer par SQLite. **Pourquoi :** 10 utilisateurs qui écrivent en même temps, un historique de toutes les modifications, et des sauvegardes quotidiennes fiables (`pg_dump`). **Rejeté :** SQLite, que recommande `_ARCHITECTURE_EXPLAINED.md` pour commencer ; il gère mal les écritures simultanées.

### ADR 3 — Docker Compose pour l'emballage
*2026-11-10.* **Décidé :** l'application et sa base tournent dans des conteneurs Docker Compose. **Pourquoi :** on ignore encore si les serveurs de l'AAN sont sous Windows ou Linux, et l'application doit pouvoir changer de serveur sans réécriture (`NFR.md` § Portabilité), y compris depuis l'hébergement temporaire de secours. **Rejeté :** une installation directe sur le serveur, qui lierait l'application à un système précis. **Dépend de :** l'accord du service informatique (§15, Q1).

### ADR 4 — Fournisseurs derrière une interface, fichiers sur disque
*2026-11-10.* **Décidé :** l'envoi des SMS passe par un adaptateur par opérateur (Digicel, Natcom) ; l'envoi des emails par SMTP configurable ; les documents de cours sont des fichiers sur le disque du serveur, dans un volume sauvegardé avec la base. **Pourquoi :** rien ne doit être codé en dur pour un fournisseur (`NFR.md` § Portabilité), et les serveurs de l'AAN suffisent pour stocker les documents. **Rejeté :** un stockage de fichiers dans le nuage, inutile pour ce volume et contraire à l'hébergement sur les serveurs de l'AAN.

### ADR 5 — Sessions côté serveur plutôt que jetons JWT
*2026-11-10.* **Décidé :** une session gardée par le serveur, identifiée par un cookie protégé, expirant après 15 minutes d'inactivité. **Pourquoi :** pour une application interne d'une dizaine d'utilisateurs, c'est plus simple, et fermer une session (compte désactivé ou bloqué) prend effet tout de suite. **Rejeté :** les jetons JWT de `fds-pay`, qu'on ne peut pas révoquer avant leur expiration sans ajouter une liste de révocation.

### ADR 6 — Un journal automatique, et protégé par la base
*2026-11-16, US-003.* **Décidé :** chaque enregistrement en base (événement `before_flush` de SQLAlchemy) ajoute ses entrées à `audit_log` dans la même transaction ; chaque table se déclare journalisée ou exemptée, et un test échoue sinon ; un déclencheur PostgreSQL refuse toute modification, suppression ou remise à zéro du journal. **Pourquoi :** « rien ne s'efface sans trace » (`PRD.md` §7) doit tenir pour toutes les tables des Epics à venir, sans dépendre de la mémoire de chacun, et même en dehors de l'application. **Rejeté :** un appel explicite au journal dans chaque fonction d'écriture (facile à oublier) ; des déclencheurs PostgreSQL pour tout le journal (ils ne connaissent pas l'auteur connecté, et se testent mal). **Limite connue :** les modifications « en bloc » de SQLAlchemy échappent au mécanisme ; elles sont proscrites (`backend/README.md` § Journal).

## 15. Questions ouvertes

> 1. Qu'est-ce qui est véritablement non résolu à l'instant, sans bloquer le démarrage, mais sans être oublié non plus ?
> 2. Qui ou quoi résoudrait chaque question ouverte, et quand ?

| # | Question | Qui la résout | Quand |
|---|---|---|---|
| Q1 | Le service informatique de l'AAN accepte-t-il Docker sur ses serveurs ? Sous quel système (Windows ou Linux) ? Y a-t-il déjà une base de données ? | L'auteur, auprès du service informatique | Avant le premier déploiement |
| Q2 | Quels fournisseurs de SMS exactement (Digicel, Natcom) et quel budget ? | L'AAN | Avant de construire la double authentification par SMS |
| Q3 | Le serveur peut-il sortir vers internet pour envoyer emails et SMS ? Sinon, quel serveur d'email interne utiliser ? | L'auteur, auprès du service informatique | Avant de construire la double authentification |

---
