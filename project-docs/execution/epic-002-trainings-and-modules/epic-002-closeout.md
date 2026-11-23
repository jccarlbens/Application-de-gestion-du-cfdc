---
created: 2026-11-20T00:00:00Z
updated: 2026-11-23T16:29:06Z
---

# Clôture de l'Epic 002 — Formations et modules

**Workstream :** WS-02 Formations et modules ; contributions à WS-05 (le journal) et WS-01 (droits)
**Statut :** ✅ Terminé — clos le 2026-11-23
**Objectif :** le CFDC a son catalogue de formations dans l'application, et chaque formateur y retrouve ses modules et ses documents.

Ce document fige ce que l'Epic a livré.
- **Le détail, user story par user story,** vit dans `project-docs/execution/EPIC_EXECUTION.md` et dans le fichier de chacune.
- **Le comportement et l'implémentation,** consolidés, sont dans `functional-specs/ws-func-02-trainings-and-modules.md` et `technical-specs/ws-tech-02-trainings-and-modules.md`.

## User stories livrées

| User story | Titre | Spec |
|---|---|---|
| US-010 | Catalogue des formations | [US-010.md](US-010.md) |
| US-011 | Modules et formateurs | [US-011.md](US-011.md) |
| US-012 | Documents de cours | [US-012.md](US-012.md) |
| US-013 | « Mes modules » du formateur | [US-013.md](US-013.md) |

Les 4 user stories sont ✅ Terminé ; vérifiées sur le serveur de test et validées par l'administrateur informatique le 2026-11-23.

## Suivi

- Milestone « Epic 2 — Formations et modules » : 4 issues sur 4 fermées (#18 à #21). Milestone fermé le 2026-11-23.
- Pull requests fusionnées : [#22](https://github.com/jccarlbens/Application-de-gestion-du-cfdc/pull/22) (affinage et US-010), [#23](https://github.com/jccarlbens/Application-de-gestion-du-cfdc/pull/23) (US-011), [#24](https://github.com/jccarlbens/Application-de-gestion-du-cfdc/pull/24) (US-012 et US-013).

## Bilan pour l'équipe

### Livré

**Le catalogue du CFDC est dans l'application.** Les formations sont rangées par domaine et sous-domaine (Sûreté-Sécurité, Accueil).
- La secrétaire, le coordonnateur et le chef de service enregistrent les formations et leurs modules, et désignent les formateurs.
- L'administrateur corrige ce qui est enregistré, gère les domaines et dépose les documents de cours (PDF, Word, PowerPoint).
- Chaque formateur trouve, dans « Mes modules », les modules qui lui sont confiés et leurs documents.
- Chaque fiche a son historique, en phrases, avec le nom de chaque auteur.

Vérifié sur le serveur de test le 2026-11-23 : les quatre user stories sont conformes.

### Qui a fait quoi

| Personne | Rôle dans l'Epic |
|---|---|
| `jccarlbens` | Auteur et administrateur informatique : réponses de l'affinage (domaines, retrait de la « formation importante »…), construction avec l'agent (commits à son nom), fusion des pull requests, tests sur le serveur et validation (2026-11-23) |
| `caleb17` | Relecteur demandé sur les pull requests #22, #23 et #24 |

Les issues n'avaient pas de personne assignée.

### Décisions

| Décision | Pourquoi |
|---|---|
| **Domaines et sous-domaines**, sur deux niveaux (Q1) | Le CFDC range ses formations ainsi : Sûreté-Sécurité › Conduite sur la rampe |
| **La « formation importante » est retirée du produit** (Q3) | Le certificat est remis sur demande ; la notion ne servait à rien d'autre. `PRD.md`, `GLOSSARY.md`, `SOLUTION_DESIGN.md` et `NFR.md` sont corrigés |
| **L'administrateur corrige directement**, en attendant l'Epic 5 (Q4) | Sans cela, une faute de frappe serait restée sans remède jusqu'aux demandes de correction |
| **Désigner un formateur « à désigner » est un complément** ; le changer est une modification (US-011) | La secrétaire complète le catalogue au fil de l'eau ; seul l'administrateur revient sur un choix |
| **Un formateur parti reste sur ses modules, signalé** (US-011) | On garde la trace de qui enseignait, et l'administrateur choisit le remplaçant |
| **Documents : 25 Mo, contenu vérifié, rien ne s'efface** (Q7, Q9) | Un fichier déguisé est refusé ; une ancienne version reste consultable par l'administrateur |
| **Pertes de fichiers acceptées sur le serveur de test** (Q8) | Render gratuit n'a pas de disque permanent ; les vraies données iront sur les serveurs de l'AAN |
| **L'accès aux documents suit le formateur actuel du module** (US-012) | L'ancien formateur n'a plus à voir les supports d'un cours qu'il ne donne plus |

### Surprises

Ce qu'on croyait, et qui s'est révélé faux. Le détail est dans les notes de réalisation ; il n'y a pas eu de fichier dans `reviews/`.
- **Le journal enregistrait des liens vides.** Quand une fiche était reliée par un objet plutôt que par son identifiant, l'entrée de création gardait la clé vide : le module d'un document, et, depuis US-003, le compte d'un rôle. Corrigé pour toutes les tables (US-012). Les entrées déjà écrites restent telles quelles, puisque le journal ne se modifie pas.
- **Nginx refusait tout fichier de plus de 1 Mo,** avec un message en anglais. La limite est relevée à 26 Mo, et le refus est en français (US-012).
- **`now()` donne la même heure à toute une transaction :** l'ordre des modules aurait dépendu du hasard. `clock_timestamp()` est utilisé à la place (US-011).
- **Un test de droits sautait sans bruit une route renommée** (l'historique) ; il échoue désormais si une route attendue manque (US-010).
- **L'outil des tests de l'interface** répondait à `/history/trainings/t-1` avec la réponse prévue pour `/trainings/t-1` ; il choisit maintenant le chemin le plus long (US-010).
- **Le nom de l'auteur dans l'historique** n'était connu que de l'administrateur et du coordonnateur ; c'est désormais le serveur qui le donne (US-010).
- **Render bloque l'envoi d'emails** par les ports 25, 465 et 587 sur son offre gratuite, depuis septembre 2025. Découvert pendant les tests, en créant un compte depuis l'écran : jusque-là, tous les emails partaient du poste de l'administrateur. Le serveur de test utilise maintenant le port 2525 (`ws-tech-01-accounts-and-access.md` § Emails).

### Points ouverts

- **La direction ne voit pas le nom d'un ancien formateur** dans l'historique quand il n'est plus sur aucun module : elle voit « Détails » à la place. Le serveur pourrait donner ces noms ; ce n'est pas demandé.
- **Les documents ne sont pas sauvegardés** sur le serveur de test ; la sauvegarde du volume `documents` viendra avec la mise en service sur les serveurs de l'AAN.
- **Pas d'antivirus** sur les documents déposés : seuls l'extension, le contenu et la taille sont vérifiés.

### Ensuite

**L'Epic 3, demandes et planification** (`epic-003-requests-and-sessions`, WS-03) : les demandes de formation, les sessions, les horaires et le calendrier. Les sessions s'appuieront sur les formations et les modules de cet Epic.

## Contributions à d'autres Workstreams

- **WS-05, le journal :** sa paire de specs est mise à jour (`ws-func-05-traceability.md`, `ws-tech-05-traceability.md`).
  - La route d'historique est commune à toutes les fiches (`GET /history/{genre}/{id}`), avec le nom de l'auteur (`actor_name`).
  - Le panneau « Historique » est devenu une entité commune (`entities/history`).
  - Les clés étrangères données par un objet sont recopiées avant la photo du journal (`_fill_foreign_keys`).
  - Une fiche peut s'inscrire dans l'historique d'une autre : modules et documents sous leur formation.
- **WS-01, droits et menus :** les menus « Formations », « Mes modules » et « Documents de cours » mènent désormais à de vrais écrans. Le test des droits vérifie les rôles exacts de chaque route.

## Contrôle de `PRD.md`, `SOLUTION_DESIGN.md` et `GLOSSARY.md`

Validé par l'administrateur le 2026-11-23 :
- `PRD.md` §6, « Enregistrer une formation » : le **sous-domaine** remplace « son domaine (sûreté, sécurité…) » ;
- `PRD.md` §6, « Déposer un document de cours » : consultable par le **formateur actuel du module** et l'administrateur ;
- `GLOSSARY.md`, exemple de **Formation** : « Conduite sur la rampe — niveau 1 », au lieu de « conduite sur le tarmac ».

`SOLUTION_DESIGN.md` §6 avait été tenu à jour par US-010 à US-012 : relu, rien d'obsolète. Les corrections de l'affinage (domaines, retrait de la « formation importante », §13 du PRD) avaient été faites le 2026-11-19.

## Où sont allées les règles de l'affinage

Voir la fin de [epic-002-refinement.md](epic-002-refinement.md).
