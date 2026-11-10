---
created: 2026-11-09T00:00:00Z
updated: 2026-11-10T16:56:06Z
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
| WS-03 | Demandes et planification | Demandes de formation, sessions, horaires, formations importantes | §6 « Demandes et planification » |
| WS-04 | Participants et suivi | Participants, inscriptions, présences, évaluations, remise des attestations et des certificats | §6 « Participants, présences et évaluations » |
| WS-05 | Corrections et traçabilité | Demandes de correction, validation par l'administrateur, historique des modifications, journal | §6 « Corrections », §7 |
| WS-06 | Consultation | Vue d'ensemble de l'unité, recherche, export Excel et PDF | §6 « Consultation », §10 |

*Validé par l'utilisateur le 2026-11-10.*

## 3. Vue d'ensemble du système

> 1. En quelques phrases, comment les pièces principales s'articulent-elles de bout en bout ?
> 2. Quel est le diagramme ou le flux unique qui expliquerait cela le plus vite à un nouvel ingénieur ?

*(À écrire)*

## 4. Carte des composants

> 1. Quels sont les composants réellement exécutables ou déployables, et qu'est-ce que chacun possède ?
> 2. Quels ports, quelles URL, quels points d'entrée chacun expose-t-il ?
> 3. Y a-t-il ici un composant qui est en réalité deux composants déguisés en un seul ?

*(À écrire)*

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
- **Les documents de cours** sont des fichiers sur le disque du serveur ; la base ne garde que leur chemin et leurs métadonnées (ADR 4).

**Les fiches.** Leurs noms de tables et de champs seront en anglais, au pluriel, en `snake_case` ; le détail des colonnes s'écrira avec les migrations.

| Fiche | Contenu principal |
|---|---|
| **Utilisateur** | badge `A00-00` (unique), nom, email, téléphone, rôles (plusieurs possibles), canal de double authentification, actif ou désactivé, bloqué ou non |
| **Formation** | intitulé, domaine, **importante ou non** (décidé par le coordonnateur pour la formation, et non pour une session) |
| **Module** | formation, titre, formateur *(à préciser : le formateur a-t-il toujours un compte ?)* |
| **Document de cours** | module, fichier (PDF, PowerPoint, Word), déposé par, date |
| **Demande de formation** | service demandeur, date de réception, formation demandée, validée par le coordonnateur |
| **Session** | formation, demande d'origine (facultative), date de début, date de fin, horaires. Une session dure **d'une heure à une semaine** |
| **Participant** | nom, prénom, **NIF ou CIN** (au moins l'un des deux, obligatoire ; il sert à reconnaître la même personne d'une session à l'autre), fonction, service ou entreprise, téléphone, interne ou externe |
| **Inscription** (un participant dans une session) | inscrit par, présence, note sur 100, commentaires, date de remise de l'attestation, date de remise du certificat |
| **Demande de correction** | fiche visée, modification ou suppression, changement proposé, demandeur, décision de l'administrateur |
| **Journal** | qui, quoi, quand, valeur avant, valeur après. Rien n'y est jamais effacé (`PRD.md` §7) |

**Les listes de référence.**
- **Domaines de formation :** une liste fixe, que l'utilisateur fournira.
- **Services de l'AAN et entreprises externes :** une liste, que l'utilisateur fournira, avec une option « Autre ». En attendant, ils se saisissent en **texte libre**.

## 7. Flux d'authentification et d'autorisation *(Conditionnelle — à sauter s'il n'y a aucun contrôle d'accès)*

> 1. Étape par étape, comment passe-t-on d'anonyme à authentifié, puis à autorisé pour une action précise ?
> 2. Qu'est-ce qui est émis (un jeton, une session, une clé), et que prouve-t-il réellement ?

*(À écrire)*

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

*(À écrire)*

## 12. Hypothèses

> 1. Qu'est-ce que cette conception suppose vrai sans que cela ait été réellement vérifié ?
> 2. Quelle hypothèse, si elle était fausse, imposerait une refonte plutôt qu'un correctif ?

*(À écrire)*

## 13. Hors périmètre

> 1. Qu'est-ce qui est architecturalement exclu de cette version, et pourquoi ?
> 2. Y a-t-il ici une exclusion qu'un Workstream ultérieur devra revisiter ?

*(À écrire)*

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

## 15. Questions ouvertes

> 1. Qu'est-ce qui est véritablement non résolu à l'instant, sans bloquer le démarrage, mais sans être oublié non plus ?
> 2. Qui ou quoi résoudrait chaque question ouverte, et quand ?

| # | Question | Qui la résout | Quand |
|---|---|---|---|
| Q1 | Le service informatique de l'AAN accepte-t-il Docker sur ses serveurs ? Sous quel système (Windows ou Linux) ? Y a-t-il déjà une base de données ? | L'auteur, auprès du service informatique | Avant le premier déploiement |
| Q2 | Quels fournisseurs de SMS exactement (Digicel, Natcom) et quel budget ? | L'AAN | Avant de construire la double authentification par SMS |

---
