---
created: 2026-11-10T00:00:00Z
updated: 2026-11-17T17:29:48Z
---

# Affinage de l'Epic 001 — Mise en place et accès

**Statut :** ✅ Clos le 2026-11-17 avec l'Epic ([epic-001-closeout.md](epic-001-closeout.md)). Ce fichier reste comme l'histoire de l'affinage ; **ses règles ont déménagé** (voir la fin).
**Workstreams :** WS-01 Comptes et accès ; WS-05 Corrections et traçabilité (le journal seulement).
**Milestone GitHub :** « Epic 1 — Mise en place et accès »

> Tant que l'Epic était ouvert, ses règles vivaient ici. Depuis la clôture, **ce fichier n'est plus la référence** : voir « Où sont allées les règles ».

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
| E1-1 | Aucun code n'existe encore : il n'y a rien à lire dans le code source. Les constats viendront de la construction | Clos : les constats de construction sont dans les notes de réalisation de chaque user story et dans le bilan de clôture |
| E1-2 | Le Milestone GitHub doit être créé à la main : l'agent n'a pas d'outil pour créer un Milestone dans cette session | Résolu : créé par l'utilisateur ; l'ajout automatique des issues au tableau n° 4 est activé |
| E1-3 | Un hébergement gratuit public pour le serveur de test contredit l'hypothèse « réseau interne seulement » (`SOLUTION_DESIGN.md` §12) si de vraies données personnelles y passent | Résolu par Q4 : données fictives seulement |

## Questions ouvertes

| # | Question | Recommandation | Réponse |
|---|---|---|---|
| Q1 | Comment créer le **premier compte administrateur**, puisque personne ne peut s'inscrire seul ? | Une commande en ligne, lancée une fois à l'installation sur le serveur | ✅ Oui (2026-11-10) |
| Q2 | Quels **tests** exiger ? | `pytest` (unitaires et intégration sur une vraie base PostgreSQL) et Vitest, lancés par GitHub Actions ; la fusion sur `main` exige qu'ils passent. Pas de seuil de couverture chiffré au départ | ✅ Oui |
| Q3 | Quel **serveur d'email** pour le développement et le serveur de test ? | Un faux serveur SMTP qui capture les emails (Mailpit) dans Docker Compose ; le vrai serveur SMTP seulement en production | ✅ Oui |
| Q4 | Où mettre le **serveur de test** tant que les serveurs de l'AAN ne sont pas accessibles ? | Sur le poste d'un membre de l'équipe avec Docker Compose, plutôt qu'un hébergement public, puisque l'application doit rester sur le réseau interne | ✅ Un **hébergement gratuit**, mais **uniquement avec des données fictives** : aucun vrai participant, NIF ou CIN n'y entre ; les vraies données n'arrivent que sur les serveurs de l'AAN. Hébergeur à choisir dans US-001 |
| Q5 | Protéger la branche `main` sur GitHub ? | Oui : GitHub Actions doit être vert et une relecture approuvée est exigée, conformément à `PROJECT_WORKFLOW.md` | ✅ Oui |
| Q6 | Y a-t-il une **charte graphique** de l'AAN (logo, couleurs, polices) pour l'interface ? | Si oui, la fournir avant l'écran de connexion ; sinon, une interface sobre aux couleurs neutres | ✅ Pas de charte formelle : interface **bleu et blanc** |
| Q7 | Que garde le **journal** pour chaque modification ? | La fiche visée, l'action, l'auteur, l'heure, et les valeurs avant et après en entier | ✅ Oui |

## Lot de user stories

*Découpage et ordre validés par l'utilisateur le 2026-11-10.*

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
| 9 | US-009 Écran de gestion des comptes | Sorti de US-002 à son affinage (2026-11-13) : liste, création, rôles, désactivation | US-002, US-007 |

**Ordre de construction à deux :** US-001 d'abord, seule. Puis US-002. Ensuite, en parallèle, US-003 pour un membre, et US-004 puis US-005 pour l'autre. Puis US-006 et US-007 en parallèle. Puis US-009. US-008 en dernier, dès que les fournisseurs SMS sont connus.

## Où sont allées les règles

*Clôture du 2026-11-17.*

| Règle | Document qui la porte désormais |
|---|---|
| Q1 — le premier administrateur se crée par une commande | `functional-specs/ws-func-01-accounts-and-access.md` § Les comptes ; `technical-specs/ws-tech-01-accounts-and-access.md` § Commandes |
| Q2 — tests `pytest` et Vitest en CI, fusion conditionnée | `technical-specs/ws-tech-01-accounts-and-access.md` § Le socle ; `PROJECT_WORKFLOW.md` |
| Q3 — Mailpit en local, vrai SMTP ailleurs (Brevo sur le serveur de test) | `technical-specs/ws-tech-01-accounts-and-access.md` § Emails ; `SOLUTION_DESIGN.md` §11 |
| Q4 — serveur de test gratuit, **données fictives seulement** | `SOLUTION_DESIGN.md` §11 ; `functional-specs/ws-func-01-accounts-and-access.md` § Le serveur de test ; `AGENTS.md` |
| Q5 — `main` protégée (CI verte, relecture approuvée) | `technical-specs/ws-tech-01-accounts-and-access.md` § Le socle |
| Q6 — interface bleu et blanc | `technical-specs/ws-tech-01-accounts-and-access.md` § Le socle (jetons `brand-*`) |
| Q7 — le journal garde l'avant et l'après en entier | `functional-specs/ws-func-05-traceability.md` ; `SOLUTION_DESIGN.md` §6 et ADR 6 |
| US-005, US-006, US-008 et leur ordre | `EPIC_EXECUTION.md` § Epic 7 ; `PLAN.md` |
