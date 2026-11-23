---
created: 2026-11-09T00:00:00Z
updated: 2026-11-23T17:25:50Z
---

# EPIC_EXECUTION.md — CFDC

**Répond à :** quel est le statut de chaque user story, à l'instant ?
**Dépend de :** `PLAN.md` pour les noms des Epics.

> **Statut : suivi dérivé, non rédigé par réflexion.** Ce fichier se remplit de lui-même à mesure que les Epics de `PLAN.md` sont travaillés et que les user stories se closent — il n'y a rien à rédiger à l'avance ici.
>
> **Contrôle à exécuter, et non contenu à imaginer :**
> 1. Ce tableau est-il encore vrai à l'instant, ou le statut d'une user story a-t-il changé sans que ce fichier soit mis à jour ?
> 2. Chaque Epic de `PLAN.md` a-t-il une section correspondante ici, dans le même ordre ?

---

## Epic 1 — Mise en place et accès

**Dossier :** `epic-001-setup-and-access/`
**Workstreams :** WS-01 Comptes et accès, WS-05 Corrections et traçabilité (le journal seulement)
**Milestone GitHub :** « Epic 1 — Mise en place et accès »
**Statut :** ✅ Terminé — clos le 2026-11-17, voir [epic-001-closeout.md](epic-001-setup-and-access/epic-001-closeout.md). US-005, US-006 et US-008 sont passées à l'Epic 7.

Le socle technique (code de départ, Docker Compose, GitHub Actions, serveur de test) et l'accès sécurisé du personnel du CFDC : comptes, rôles, connexion par badge, double authentification, blocage, déconnexion automatique, mot de passe oublié, et le journal des modifications.

**Affinage :** [epic-001-refinement.md](epic-001-setup-and-access/epic-001-refinement.md) — clos ; ses règles ont rejoint `functional-specs/ws-func-01-accounts-and-access.md`, `technical-specs/ws-tech-01-accounts-and-access.md` et la paire WS-05 (journal).

**Ordre de construction :** US-001 seule, d'abord ; puis US-002 ; ensuite, en parallèle, US-003 pour un membre, US-004 puis US-005 pour l'autre ; puis US-006 et US-007 en parallèle ; puis US-009 (écran des comptes, sorti de US-002 le 2026-11-13) ; US-008 en dernier (Should).

*Changé le 2026-11-17, à la demande de l'administrateur :* **US-005** (double authentification par email) et **US-006** (mot de passe oublié) passent **après US-007**. Elles restent **obligatoires avant la mise en service** (`PLAN.md`, Must ; `PRD.md` §12) : reportées, pas abandonnées.

| User story | Titre | Statut | Spec |
|---|---|---|---|
| US-001 | Mise en place | ✅ Terminé | [US-001.md](epic-001-setup-and-access/US-001.md) |
| US-002 | Comptes utilisateurs | ✅ Terminé | [US-002.md](epic-001-setup-and-access/US-002.md) |
| US-003 | Journal des modifications | ✅ Terminé | [US-003.md](epic-001-setup-and-access/US-003.md) |
| US-004 | Connexion et session | ✅ Terminé | [US-004.md](epic-001-setup-and-access/US-004.md) |
| US-007 | Droits et navigation par rôle | ✅ Terminé | [US-007.md](epic-001-setup-and-access/US-007.md) |
| US-009 | Écran de gestion des comptes | ✅ Terminé | [US-009.md](epic-001-setup-and-access/US-009.md) |

*Changé le 2026-11-17, à la clôture :* US-005, US-006 et US-008 sont passées à l'**Epic 7 — Sécurité avant la mise en service**, avec leurs fichiers et leurs issues.

---

## Epic 2 — Formations et modules

**Dossier :** `epic-002-trainings-and-modules/`
**Workstream :** WS-02 Formations et modules
**Milestone GitHub :** « Epic 2 — Formations et modules »
**Statut :** ✅ Terminé — clos le 2026-11-23, voir [epic-002-closeout.md](epic-002-trainings-and-modules/epic-002-closeout.md)

Le catalogue des formations, leurs modules et leurs formateurs, et les documents de cours (`PRD.md` §6 « Formations, modules et documents »). **Objectif :** le CFDC a son catalogue de formations dans l'application, et chaque formateur y retrouve ses modules et ses documents. Comportement et implémentation, une fois livrés : `functional-specs/ws-func-02-*.md` et `technical-specs/ws-tech-02-*.md`.

**Ordre de construction :** US-010 d'abord ; puis US-011 ; ensuite US-012 et US-013 en parallèle (US-013 affiche les documents dès que US-012 est fusionnée).

**Affinage :** [epic-002-refinement.md](epic-002-trainings-and-modules/epic-002-refinement.md) — clos ; ses règles ont rejoint `functional-specs/ws-func-02-trainings-and-modules.md`, `technical-specs/ws-tech-02-trainings-and-modules.md`, `PRD.md`, `GLOSSARY.md` et `SOLUTION_DESIGN.md`.

| User story | Titre | Statut | Spec |
|---|---|---|---|
| US-010 | Catalogue des formations | ✅ Terminé | [US-010.md](epic-002-trainings-and-modules/US-010.md) |
| US-011 | Modules et formateurs | ✅ Terminé | [US-011.md](epic-002-trainings-and-modules/US-011.md) |
| US-012 | Documents de cours | ✅ Terminé | [US-012.md](epic-002-trainings-and-modules/US-012.md) |
| US-013 | « Mes modules » du formateur | ✅ Terminé | [US-013.md](epic-002-trainings-and-modules/US-013.md) |

---

## Epic 3 — Demandes et planification

**Dossier :** `epic-003-requests-and-sessions/`
**Workstream :** WS-03 Demandes et planification
**Milestone GitHub :** « Epic 3 — Demandes et planification »
**Statut :** 🟡 En cours — affinage confirmé le 2026-11-23 ; 4 user stories à faire

Les demandes de formation, la planification des sessions, les horaires et le calendrier (`PRD.md` §6 « Demandes et planification »). **Objectif :** le coordonnateur enregistre les demandes validées et planifie les sessions dans l'application plutôt que sur papier. Comportement et implémentation, une fois livrés : `functional-specs/ws-func-03-*.md` et `technical-specs/ws-tech-03-*.md`.

**Ordre de construction :** US-014 et US-015 en parallèle (le lien entre une session et une demande se branche en dernier) ; puis US-016 ; puis US-017.

**Affinage :** [epic-003-refinement.md](epic-003-requests-and-sessions/epic-003-refinement.md) — en cours ; les questions ouvertes, les règles de l'Epic tant qu'il est ouvert, et le lot de user stories dans l'ordre de construction.

| User story | Titre | Statut | Spec |
|---|---|---|---|
| US-014 | Demandes de formation | 🔲 À faire | [US-014.md](epic-003-requests-and-sessions/US-014.md) |
| US-015 | Sessions | 🔲 À faire | [US-015.md](epic-003-requests-and-sessions/US-015.md) |
| US-016 | Horaires des sessions | 🔲 À faire | [US-016.md](epic-003-requests-and-sessions/US-016.md) |
| US-017 | Calendrier des sessions | 🔲 À faire | [US-017.md](epic-003-requests-and-sessions/US-017.md) |

---

## Epic 7 — Sécurité avant la mise en service

**Dossier :** `epic-007-pre-production-security/`
**Workstream :** WS-01 Comptes et accès
**Milestone GitHub :** « Epic 7 — Sécurité avant la mise en service »
**Statut :** ⏳ Pas démarré — placé en dernier, avant la mise en service

Ce qui manque encore à l'accès pour passer en production : la double authentification par email, le mot de passe oublié et, si le budget le permet, la double authentification par SMS. Ces user stories viennent de l'Epic 1 ; elles ont été reportées le 2026-11-17 pour avancer sur le métier. **US-005 et US-006 sont obligatoires avant la mise en service** (Must).

**Affinage :** pas encore fait. Les trois fiches ont été écrites à l'affinage de l'Epic 1 ([epic-001-refinement.md](epic-001-setup-and-access/epic-001-refinement.md)) et seront affinées une par une avant construction.

**Ordre de construction :** US-005 et US-006 en parallèle ; US-008 ensuite, dès que les fournisseurs SMS sont connus (`SOLUTION_DESIGN.md` §15, Q2).

| User story | Titre | Statut | Spec |
|---|---|---|---|
| US-005 | Double authentification par email | 🔲 À faire | [US-005.md](epic-007-pre-production-security/US-005.md) |
| US-006 | Mot de passe oublié | 🔲 À faire | [US-006.md](epic-007-pre-production-security/US-006.md) |
| US-008 | Double authentification par SMS *(Should)* | 🔲 À faire | [US-008.md](epic-007-pre-production-security/US-008.md) |
