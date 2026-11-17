---
created: 2026-11-17T00:00:00Z
updated: 2026-11-17T17:29:48Z
---

# Clôture de l'Epic 001 — Mise en place et accès

**Workstreams :** WS-01 Comptes et accès ; WS-05 Corrections et traçabilité (le journal seulement)
**Statut :** ✅ Terminé — clos le 2026-11-17
**Objectif :** le personnel du CFDC peut se connecter en sécurité, et toute action laisse une trace.

Ce document fige ce que l'Epic a livré.
- **Le détail, user story par user story,** vit dans `project-docs/execution/EPIC_EXECUTION.md` et dans le fichier de chacune ; il n'est pas recopié ici.
- **Le comportement et l'implémentation,** consolidés, sont dans :
  - `functional-specs/ws-func-01-accounts-and-access.md` et `technical-specs/ws-tech-01-accounts-and-access.md` ;
  - `functional-specs/ws-func-05-traceability.md` et `technical-specs/ws-tech-05-traceability.md`, pour le journal seulement.

## User stories livrées

| User story | Titre | Spec |
|---|---|---|
| US-001 | Mise en place | [US-001.md](US-001.md) |
| US-002 | Comptes utilisateurs | [US-002.md](US-002.md) |
| US-003 | Journal des modifications | [US-003.md](US-003.md) |
| US-004 | Connexion et session | [US-004.md](US-004.md) |
| US-007 | Droits et navigation par rôle | [US-007.md](US-007.md) |
| US-009 | Écran de gestion des comptes | [US-009.md](US-009.md) |

Ces 6 user stories sont ✅ Terminé ; l'administrateur informatique les a validées le 2026-11-17.

**L'Epic a grossi en cours de route :** US-009 (écran des comptes) a été sortie de US-002 à son affinage, le 2026-11-13. Un écran construit avant la connexion (US-004) et les droits (US-007) n'aurait su ni qui l'utilise, ni comment le protéger.

## Déplacé vers l'Epic 7

Ces user stories n'ont **pas été abandonnées** : le 2026-11-17, l'administrateur a décidé de clore l'Epic 1 sans elles, pour avancer sur le métier. Elles forment l'**Epic 7 — Sécurité avant la mise en service**, placé en dernier dans `PLAN.md`, et **doit être terminé avant toute mise en service**. Leurs fichiers ont été déplacés dans `epic-007-pre-production-security/` et leurs issues ont changé de Milestone.

| User story | Titre | Priorité | Pourquoi elle peut attendre |
|---|---|---|---|
| US-005 | Double authentification par email | Must | Le serveur de test ne contient que des données fictives |
| US-006 | Mot de passe oublié | Must | En attendant, l'administrateur peut recréer un accès |
| US-008 | Double authentification par SMS | Should | Fournisseurs et budget inconnus (`SOLUTION_DESIGN.md` §15, Q2) |

## Suivi

- **Milestone « Epic 1 — Mise en place et accès »** clos le 2026-11-17 : 6 issues sur 6 fermées.
- **Réconciliation :** l'issue de US-009 ([#10](https://github.com/jccarlbens/Application-de-gestion-du-cfdc/issues/10)) était restée ouverte après la fusion de sa pull request, qui ne la fermait pas d'elle-même ; elle a été fermée à la clôture, avec un commentaire.
- **Changement de Milestone :** les issues [#5](https://github.com/jccarlbens/Application-de-gestion-du-cfdc/issues/5), [#6](https://github.com/jccarlbens/Application-de-gestion-du-cfdc/issues/6) et [#8](https://github.com/jccarlbens/Application-de-gestion-du-cfdc/issues/8) passent au Milestone « Epic 7 — Sécurité avant la mise en service ».

## Bilan pour l'équipe

### Livré

**L'application a un socle complet et un accès sécurisé.**
- Elle se lance en local par `docker compose up`.
- Elle se teste à chaque pull request : `main` n'accepte qu'une CI verte et une relecture approuvée.
- Elle tourne sur un **serveur de test** (Render et Neon), **avec des données fictives seulement**.

**Le personnel peut désormais :**
- recevoir un compte, créé par l'administrateur ou le coordonnateur, et choisir son mot de passe par un lien envoyé par email ;
- se connecter par **numéro de badge** et mot de passe, avec un blocage après 5 échecs et une déconnexion après 15 minutes d'inactivité ;
- voir l'accueil et les menus de ses rôles ;
- **pour l'administrateur et le coordonnateur,** gérer les comptes depuis l'écran « Comptes », chaque compte ayant son historique en phrases.

**Toute modification laisse une trace** dans un journal que personne ne peut modifier, pas même directement dans la base.

### Qui a fait quoi

| Personne | Rôle dans l'Epic |
|---|---|
| `jccarlbens` | Auteur et administrateur informatique : décisions d'affinage, construction avec l'agent (tous les commits sont à son nom depuis le 2026-11-12), mise en place de Neon, Render et Brevo, vérifications sur le serveur de test, validation de chaque user story |
| `caleb17` | Relecteur demandé sur les pull requests |

Les issues n'avaient pas de personne assignée.

### Décisions

| Décision | Pourquoi |
|---|---|
| **Serveur de test sur Render et Neon**, données fictives seulement | Les serveurs de l'AAN ne sont pas encore accessibles ; la base gratuite de Render expire après 30 jours |
| **Compte créé sans mot de passe**, avec un lien par email valable 48 heures | Personne ne connaît le mot de passe d'un autre |
| **L'email part dans la même transaction** que la création du compte | Un compte sans mot de passe et sans lien ne pourrait plus servir, puisque rien ne se supprime |
| **Journal automatique**, dans la même transaction, protégé par la base (ADR 6) | « Rien ne s'efface sans trace » doit tenir pour toutes les tables à venir, sans dépendre de la mémoire de chacun |
| **Sessions côté serveur**, cookie `SameSite=Strict` (ADR 5) | Une session se ferme immédiatement quand un compte est bloqué ou désactivé |
| **Pas de limite par adresse IP** | Risque accepté pour la V1 (`NFR.md` § Risques) : le blocage par compte suffit sur un réseau interne |
| **Deux niveaux de droits** : chaque route déclare ses rôles, la BLL garde les règles fines | Un test voit une route qui aurait oublié son contrôle |
| **Clore l'Epic 1 sans la double authentification ni le mot de passe oublié** (Epic 7) | Avancer sur le métier ; aucune vraie donnée avant leur livraison |

### Surprises

Ce qu'on croyait, et qui s'est révélé faux. Le détail est dans les notes de réalisation de chaque user story ; il n'y a pas eu de fichier dans `reviews/`.
- **Un test de sécurité passait sans rien vérifier.** Depuis FastAPI 0.16x, les routes d'un routeur inclus ne figurent plus une par une dans `app.routes`. Le test « aucune route n'écrit dans le journal » ne trouvait donc aucune route, et passait. Les tests de routes vérifient maintenant d'abord qu'ils trouvent des routes (US-007).
- **Les échecs de connexion arrivés à la même heure** qu'une réussite n'étaient pas comptés. Ils se comparent désormais par numéro et non par heure (US-004).
- **L'ordre des entrées du journal changeait d'un passage à l'autre**, parce que SQLAlchemy ne garantit aucun ordre. Un tri fixe a été ajouté (US-003).
- **Des tests supposaient une base vide.** Or le journal, par construction, ne se vide jamais : les tests ne regardent plus que ce qu'ils créent (US-003, US-007).
- **Un commit a été poussé avec 7 tests en échec**, parce que les commandes s'enchaînaient sans s'arrêter à l'échec. Depuis, on ne pousse qu'après des tests verts (US-003).
- **Une erreur 502 sans message** venait de Render, le temps que le backend gratuit se réveille. L'interface l'explique désormais (US-002).
- **Certains réseaux filtrent la base (port 5432) et le SMTP (ports 587 et 2525).** Ce n'était ni le code ni les réglages : tout a marché depuis une autre connexion (US-003).

### Points ouverts

- **L'Epic 7** (US-005, US-006, US-008) doit être terminé avant la mise en service.
- **Questions au service informatique de l'AAN** (`SOLUTION_DESIGN.md` §15) :
  - Q1 : Docker, système des serveurs, base existante ;
  - Q3 : sortie vers internet pour les emails.
- **Un lien de mot de passe expiré ne peut pas être renvoyé :** le mot de passe oublié (US-006) comblera ce manque.
- **Proposition restée sans réponse :** envoyer les emails en SMTP chiffré sur le port 465, pour les réseaux qui filtrent 587 et 2525.

### Ensuite

**L'Epic 2 — formations et modules** (`epic-002-trainings-and-modules`, WS-02) : le catalogue des formations, leurs modules et formateurs, et les documents de cours. Il se branchera sur les menus « Formations », « Mes modules » et « Documents de cours », et chacune de ses tables sur le journal.

## Contributions à d'autres Workstreams

- **WS-05 (journal seulement)** a sa propre paire de specs, parce que le journal est un sujet complet. Chaque fichier dit en en-tête qu'il ne couvre pas encore les demandes de correction (Epic 5).
- **Le socle technique** (US-001) sert à tous les Workstreams ; il est décrit en tête de `ws-tech-01-accounts-and-access.md`.
