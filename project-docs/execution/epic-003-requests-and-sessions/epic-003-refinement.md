---
created: 2026-11-23T00:00:00Z
updated: 2026-11-23T16:31:09Z
---

# Affinage de l'Epic 003 — Demandes et planification

**Statut :** 🟡 Ouvert — questions posées le 2026-11-23, en attente des réponses.
**Workstream :** WS-03 Demandes et planification.
**Milestone GitHub :** « Epic 3 — Demandes et planification »

> Tant que l'Epic est ouvert, **ses règles vivent ici**. À la clôture, chacune part vers le document qui possède les règles de son genre.

## Périmètre

`PRD.md` §3 (parcours, étapes 1 à 3) et §6 « Demandes et planification » :
- les **demandes de formation** : la requête écrite d'un service, validée par le coordonnateur, enregistrée puis ajustée ;
- les **sessions** : une occurrence datée d'une formation, d'une heure à une semaine, en réponse à une demande ou non ;
- les **horaires** d'une session, arrangés par les chefs de service du CFDC ;
- le **calendrier** des sessions (menu « Sessions et calendrier »).

Hors de cet Epic : les participants, les présences et les évaluations (Epic 4) ; les demandes de correction (Epic 5) ; la vue d'ensemble, la recherche et l'export (Epic 6).

## Constats

*Issus de la lecture des documents et du code, le 2026-11-23.*

| Id | Constat | Statut |
|---|---|---|
| E3-1 | **`PRD.md` §5 se contredit sur la secrétaire et les sessions.** « Enregistrer formations, sessions… » lui est permis, mais « Planifier une session (date, période) » ne l'est pas : seuls le coordonnateur et l'administrateur planifient | Ouvert — Q1 |
| E3-2 | **Une demande est-elle enregistrée avant ou après sa validation ?** Le PRD dit que le coordonnateur la valide **puis** la fait enregistrer (§3, §6). Mais la vue d'ensemble doit montrer « les demandes en attente » (§4, §6) : il faudrait donc enregistrer aussi les demandes pas encore validées | Ouvert — Q2 |
| E3-3 | **Ajuster une demande contredit la règle générale.** `PRD.md` §6 permet à la secrétaire et au coordonnateur de **modifier** une demande, alors que §2 et §7 réservent toute modification à l'administrateur. Même question pour une session dont la date change | Ouvert — Q3 |
| E3-4 | **La liste des services de l'AAN et des entreprises n'a jamais été fournie** (`SOLUTION_DESIGN.md` §6 : texte libre en attendant). Le service demandeur se saisirait donc en texte libre | Ouvert — Q4 |
| E3-5 | **La forme des « horaires » n'est décrite nulle part.** Une session dure d'une heure à une semaine, mais rien ne dit si l'horaire est un créneau par jour, par module, avec quel formateur | Ouvert — Q6 |
| E3-6 | **Une session « terminée » servira à l'Epic 4** : après elle, seul l'administrateur ajoute un participant (`PRD.md` §7). Sa date de fin doit donc être fiable | Constat |
| E3-7 | **Annuler ou reporter une session** n'est prévu nulle part. Supprimer serait contraire à « rien ne s'efface » | Ouvert — Q7 |
| E3-8 | **Les dates et heures d'une session sont des heures locales d'Haïti** (une session de 8 h à 12 h), pas des instants. La convention du projet (horodatages en UTC) vaut pour les traces ; les dates et heures prévues se garderont **sans fuseau**, en heure locale de l'AAN | Constat — décision technique, à confirmer dans `SOLUTION_DESIGN.md` |
| E3-9 | **Les menus existent depuis US-007** : « Demandes de formation » et « Sessions et calendrier », pour tous les rôles sauf le formateur. Ils mènent à « Bientôt disponible ». Le formateur, lui, n'a rien sur ses sessions | Ouvert — Q9 |
| E3-10 | **Le journal et l'historique s'appliquent tels quels** (WS-05) : chaque nouvelle table se journalise, et `_READERS` reçoit les nouvelles fiches | Constat |
| E3-11 | **`PRD.md` §6 garde « conduite sur le tarmac »** en exemple de formation (§ Organisation des formations), alors que `GLOSSARY.md` a été corrigé le 2026-11-23. Et la liste « Ce que tout le monde supposera » dit encore « Aucune notification en dehors de la double authentification » | Ouvert — Q11 |

## Questions ouvertes

| # | Question | Recommandation | Réponse |
|---|---|---|---|
| Q1 | **Qui planifie une session** (crée la session, fixe ses dates) ? | Le **coordonnateur et l'administrateur** seulement, comme le dit la ligne « Planifier une session » ; la secrétaire voit les sessions et, à l'Epic 4, y enregistre les participants. On corrige la ligne « Enregistrer formations, sessions… » du §5 | |
| Q2 | **Statut d'une demande** | Une demande s'enregistre **dès sa réception**, avec un statut : **en attente → validée** (ou **refusée**), décidé par le coordonnateur. Les demandes en attente nourriront la vue d'ensemble | |
| Q3 | **Ajuster une demande ou une session** déjà enregistrée | Exception assumée à la règle générale : la secrétaire et le coordonnateur **ajustent une demande** ; le coordonnateur **change les dates** d'une session ; chaque changement est journalisé et visible dans l'historique. Les autres corrections passent par l'administrateur, comme pour les formations | |
| Q4 | **Service demandeur** | Texte libre pour l'instant, avec une case **interne à l'AAN / entreprise externe** ; la liste viendra plus tard. Ou donnez-moi la liste maintenant | |
| Q5 | **Champs d'une demande** | Service demandeur, interne ou externe, date de réception, formation demandée (du catalogue), **nombre de participants prévu**, période souhaitée (facultative, texte), commentaire | |
| Q6 | **Forme des horaires** | Une session a des **créneaux** : date, heure de début, heure de fin, **module** (facultatif). Le formateur d'un créneau est celui du module. Les chefs de service du CFDC et le coordonnateur les arrangent | |
| Q7 | **Annuler ou reporter une session** | **Reporter** = changer ses dates (journalisé). **Annuler** = un statut « annulée », avec un motif ; la session reste visible et ne se supprime pas | |
| Q8 | **Une demande, plusieurs sessions ?** | Oui : une demande peut donner lieu à **plusieurs sessions** (par exemple 40 personnes en deux groupes) ; une session répond à **une demande au plus** | |
| Q9 | **Le formateur voit-il ses sessions** (dates, créneaux de ses modules) ? | Oui, dans « Mes modules » : les prochains créneaux de chacun de ses modules. Sinon, cela attend l'Epic 6 | |
| Q10 | **Forme du calendrier** | Une vue **par mois** (grille), avec, sur téléphone, une **liste** des sessions à venir ; filtres par domaine et par statut. Pas de glisser-déposer | |
| Q11 | Corriger `PRD.md` §6 : l'exemple « conduite sur le tarmac » et la phrase sur les notifications ? | Oui : « Conduite sur la rampe — niveau 1 », et « Aucune notification en dehors des emails d'accès » | |
| Q12 | **Conflits** : signaler un formateur prévu sur deux créneaux qui se chevauchent ? | Oui, un **avertissement** (pas un refus) à l'enregistrement d'un créneau. Les salles ne sont pas suivies (`PRD.md` §13) | |

## Lot de user stories proposé

*À valider après les réponses.* Les numéros continuent ceux du projet (dernier : US-013).

| Ordre | User story | Périmètre en une ligne | Dépend de |
|---|---|---|---|
| 1 | US-014 Demandes de formation | Enregistrer une demande à sa réception, la valider ou la refuser, l'ajuster ; écran « Demandes de formation » ; historique | — |
| 2 | US-015 Sessions | Planifier une session d'une formation (dates de début et de fin), liée ou non à une demande ; reporter, annuler ; fiche de la session et historique | US-014 pour le lien à une demande |
| 3 | US-016 Horaires | Les créneaux d'une session (date, heures, module), arrangés par les chefs de service et le coordonnateur ; avertissement de chevauchement d'un formateur | US-015 |
| 4 | US-017 Calendrier | Le calendrier des sessions (mois, et liste sur téléphone), avec filtres ; menu « Sessions et calendrier » ; selon Q9, les créneaux du formateur dans « Mes modules » | US-015, US-016 |

**Ordre de construction à deux :** US-014 et US-015 en parallèle (le lien entre une session et une demande se branche en dernier) ; puis US-016 ; puis US-017.
