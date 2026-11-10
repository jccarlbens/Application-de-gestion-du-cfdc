---
created: 2026-11-10T00:00:00Z
updated: 2026-11-10T17:13:09Z
---

# Affinage de l'Epic 001 — Mise en place et accès

**Statut :** 🟡 Ouvert — en cours d'affinage avec l'utilisateur.
**Workstreams :** WS-01 Comptes et accès ; WS-05 Corrections et traçabilité (le journal seulement).
**Milestone GitHub :** « Epic 1 — Mise en place et accès »

> Tant que l'Epic est ouvert, **ses règles vivent ici**. À la clôture, chacune part vers le document qui possède les règles de son genre.

## Périmètre

Tout ce dont les Epics suivants ont besoin pour exister : le code de départ (backend, frontend), Docker Compose, GitHub Actions, un serveur de test, et l'accès sécurisé du personnel du CFDC :
- comptes et rôles ;
- connexion par badge et mot de passe ;
- double authentification ;
- blocage après 5 échecs ;
- déconnexion après 15 minutes ;
- mot de passe oublié ;
- le **journal des modifications**, pour que tout ce qui sera construit ensuite laisse une trace.

## Constats

| Id | Constat | Statut |
|---|---|---|
| E1-1 | Aucun code n'existe encore : il n'y a rien à lire dans le code source. Les constats viendront de la construction | Ouvert |
| E1-2 | Le Milestone GitHub doit être créé à la main : l'agent n'a pas d'outil pour créer un Milestone dans cette session | Ouvert |

## Questions ouvertes

| # | Question | Recommandation | Réponse |
|---|---|---|---|
| Q1 | Comment créer le **premier compte administrateur**, puisque personne ne peut s'inscrire seul ? | Une commande en ligne, lancée une fois à l'installation sur le serveur | — |
| Q2 | Quels **tests** exiger ? | `pytest` (unitaires et intégration sur une vraie base PostgreSQL) et Vitest, lancés par GitHub Actions ; la fusion sur `main` exige qu'ils passent. Pas de seuil de couverture chiffré au départ | — |
| Q3 | Quel **serveur d'email** pour le développement et le serveur de test ? | Un faux serveur SMTP qui capture les emails (Mailpit) dans Docker Compose ; le vrai serveur SMTP seulement en production | — |
| Q4 | Où mettre le **serveur de test** tant que les serveurs de l'AAN ne sont pas accessibles ? | Sur le poste d'un membre de l'équipe avec Docker Compose, plutôt qu'un hébergement public, puisque l'application doit rester sur le réseau interne | — |
| Q5 | Protéger la branche `main` sur GitHub ? | Oui : GitHub Actions doit être vert et une relecture approuvée est exigée, conformément à `PROJECT_WORKFLOW.md` | — |
| Q6 | Y a-t-il une **charte graphique** de l'AAN (logo, couleurs, polices) pour l'interface ? | Si oui, la fournir avant l'écran de connexion ; sinon, une interface sobre aux couleurs neutres | — |
| Q7 | Que garde le **journal** pour chaque modification ? | La fiche visée, l'action, l'auteur, l'heure, et les valeurs avant et après en entier | — |

## Lot de user stories proposé

| Ordre | User story | Périmètre en une ligne | Dépend de |
|---|---|---|---|
| 1 | US-001 Mise en place | Squelettes backend et frontend, Docker Compose (application, PostgreSQL, Mailpit), GitHub Actions, serveur de test | — |
| 2 | US-002 Comptes utilisateurs | Fiche utilisateur (badge `A00-00`, nom, email, téléphone, rôles multiples) ; création par l'admin ou le coordonnateur ; désactivation et changement de rôle par l'admin ; premier admin par commande | US-001 |
| 3 | US-003 Journal des modifications | Journal (qui, quoi, quand, avant, après), branché sur les comptes, prêt pour toutes les fiches suivantes | US-002 |
| 4 | US-004 Connexion et session | Badge et mot de passe (8 caractères dont un chiffre), blocage après 5 échecs et déblocage par l'admin, session serveur de 15 minutes, déconnexion | US-002 |
| 5 | US-005 Double authentification par email | Code à 5 minutes et usage unique, code de secours donné par l'admin | US-004 |
| 6 | US-006 Mot de passe oublié | Réinitialisation par email | US-004 |
| 7 | US-007 Droits et navigation par rôle | Vérification des droits côté serveur, écran d'accueil et menus selon le ou les rôles | US-004 |
| 8 | US-008 Double authentification par SMS *(Should)* | Digicel et Natcom, choix du canal, bascule automatique sur l'autre canal | US-005 ; `SOLUTION_DESIGN.md` §15 Q2 |

**Ordre de construction à deux :** US-001 d'abord, seule. Puis US-002. Ensuite, en parallèle, US-003 pour un membre, et US-004 puis US-005 pour l'autre. Puis US-006 et US-007 en parallèle. US-008 en dernier, dès que les fournisseurs SMS sont connus.
