---
created: 2026-11-09T00:00:00Z
updated: 2026-11-17T17:22:47Z
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
**Statut :** 🟡 En cours — US-001, US-002, US-003, US-004, US-007 et US-009 terminées (2026-11-17) ; restent US-005, US-006 et US-008

Le socle technique (code de départ, Docker Compose, GitHub Actions, serveur de test) et l'accès sécurisé du personnel du CFDC : comptes, rôles, connexion par badge, double authentification, blocage, déconnexion automatique, mot de passe oublié, et le journal des modifications.

**Affinage :** [epic-001-refinement.md](epic-001-setup-and-access/epic-001-refinement.md) — les questions ouvertes, les règles de l'Epic tant qu'il est ouvert, et le lot de user stories dans l'ordre de construction.

**Ordre de construction :** US-001 seule, d'abord ; puis US-002 ; ensuite, en parallèle, US-003 pour un membre, US-004 puis US-005 pour l'autre ; puis US-006 et US-007 en parallèle ; puis US-009 (écran des comptes, sorti de US-002 le 2026-11-13) ; US-008 en dernier (Should).

*Changé le 2026-11-17, à la demande de l'administrateur :* **US-005** (double authentification par email) et **US-006** (mot de passe oublié) passent **après US-007**. Elles restent **obligatoires avant la mise en service** (`PLAN.md`, Must ; `PRD.md` §12) : reportées, pas abandonnées.

| User story | Titre | Statut | Spec |
|---|---|---|---|
| US-001 | Mise en place | ✅ Terminé | [US-001.md](epic-001-setup-and-access/US-001.md) |
| US-002 | Comptes utilisateurs | ✅ Terminé | [US-002.md](epic-001-setup-and-access/US-002.md) |
| US-003 | Journal des modifications | ✅ Terminé | [US-003.md](epic-001-setup-and-access/US-003.md) |
| US-004 | Connexion et session | ✅ Terminé | [US-004.md](epic-001-setup-and-access/US-004.md) |
| US-005 | Double authentification par email | 🔲 À faire | [US-005.md](epic-001-setup-and-access/US-005.md) |
| US-006 | Mot de passe oublié | 🔲 À faire | [US-006.md](epic-001-setup-and-access/US-006.md) |
| US-007 | Droits et navigation par rôle | ✅ Terminé | [US-007.md](epic-001-setup-and-access/US-007.md) |
| US-008 | Double authentification par SMS *(Should)* | 🔲 À faire | [US-008.md](epic-001-setup-and-access/US-008.md) |
| US-009 | Écran de gestion des comptes | ✅ Terminé | [US-009.md](epic-001-setup-and-access/US-009.md) |
