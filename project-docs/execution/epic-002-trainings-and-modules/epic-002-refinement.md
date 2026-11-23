---
created: 2026-11-17T00:00:00Z
updated: 2026-11-23T16:29:06Z
---

# Affinage de l'Epic 002 — Formations et modules

**Statut :** ✅ Clos le 2026-11-23 avec l'Epic ([epic-002-closeout.md](epic-002-closeout.md)). Ce fichier reste comme l'histoire de l'affinage ; **ses règles ont déménagé** (voir la fin).
**Workstream :** WS-02 Formations et modules.
**Milestone GitHub :** « Epic 2 — Formations et modules »

> Tant que l'Epic était ouvert, ses règles vivaient ici. Depuis la clôture, **ce fichier n'est plus la référence** : voir « Où sont allées les règles ».

## Périmètre

Le catalogue du CFDC dans l'application (`PRD.md` §6 « Formations, modules et documents ») :
- les **formations**, rangées par **domaine et sous-domaine** ;
- leurs **modules**, chacun confié à **un seul formateur** ;
- les **documents de cours** (PDF, PowerPoint, Word), déposés par l'administrateur informatique ;
- l'écran **« Mes modules »** du formateur.

Hors de cet Epic : les sessions et les demandes (Epic 3), les participants (Epic 4), les demandes de correction (Epic 5).

## Constats

*Issus de la lecture du code et des documents, le 2026-11-17.*

| Id | Constat | Statut |
|---|---|---|
| E2-1 | **La liste des domaines n'a jamais été fournie** (`GLOSSARY.md` : « liste fixe, à fournir » ; `SOLUTION_DESIGN.md` §6). Sans elle, on ne peut pas enregistrer de formation | Résolu — Q1 |
| E2-2 | **Une formation enregistrée ne peut être corrigée que par une demande de correction validée par l'administrateur** (`PRD.md` §7), et les demandes de correction n'arrivent qu'avec l'Epic 5. D'ici là, une faute de frappe dans un intitulé resterait sans remède | Résolu — Q4 |
| E2-3 | **Un formateur doit avoir un compte**, donc un numéro de badge AAN (`[A-Z]\d{2}-\d{2}`). Si un formateur vient de l'extérieur (concessionnaire, prestataire), il n'a pas de badge AAN | Résolu — Q5 |
| E2-4 | **Sur le serveur de test (Render gratuit), les fichiers déposés sont perdus à chaque redémarrage** (accepté à US-001). Les documents de cours n'y survivront pas ; en local et sur les serveurs de l'AAN, le volume `documents` de `docker-compose.yml` est déjà prévu | Résolu — Q8 |
| E2-5 | **`PRD.md` §6 range « marquer une formation comme importante » dans « Demandes et planification »**, mais `SOLUTION_DESIGN.md` §6 en fait un champ de la formation, décidé par le coordonnateur, et non de la session | Résolu — Q3 |
| E2-6 | Les menus existent déjà depuis US-007 : « Formations » (tous sauf le formateur), « Mes modules » (formateur seul), « Documents de cours » (administrateur seul). Ils mènent aujourd'hui à « Bientôt disponible » ; cet Epic les remplit | Constat |
| E2-7 | Le journal (US-003) s'applique tel quel : chaque nouvelle table devra être journalisée ou exemptée, et `bll_history._READERS` recevra les nouvelles fiches | Constat |
| E2-8 | `PRD.md` §13 dit encore « pas de notifications, sauf les codes de double authentification », alors que §6 a été corrigé à la clôture de l'Epic 1 (les emails servent à l'accès en général) | Résolu — Q11 |
| E2-9 | Aucune limite de taille de fichier n'est fixée (`NFR.md` muet) | Résolu — Q7 |

## Questions ouvertes

| # | Question | Recommandation | Réponse |
|---|---|---|---|
| Q1 | **Les domaines de formation** : quelle liste ? | Vous me la donnez maintenant (par exemple sûreté, sécurité, …) ; elle est chargée par la migration et ne change que par l'administrateur | ✅ **Deux niveaux** (2026-11-19) : **Sûreté-Sécurité** → Sensibilisation sur la carte d'accès, Conduite sur la rampe, Formation des policiers ; **Accueil** → Protocole, Civilité. Chargés par la migration ; ensuite, seul l'administrateur ajoute un domaine ou un sous-domaine |
| Q2 | **Les champs d'une formation** au-delà de l'intitulé, du domaine et de « importante » ? | Ajouter une **description** facultative ; **intitulé unique**. Pas de durée ici : elle dépend de la session (Epic 3) | ✅ Oui : description facultative, intitulé unique |
| Q3 | **« Formation importante »** : dans cet Epic, et qui la coche ? | Dans cet Epic, champ de la formation ; **le coordonnateur et l'administrateur** seulement | ✅ **Non : la notion est retirée du produit.** Le certificat reste, remis **sur demande** (noté à l'Epic 4). `PRD.md`, `GLOSSARY.md`, `SOLUTION_DESIGN.md` et `NFR.md` corrigés le 2026-11-19 |
| Q4 | **Corriger une formation, un module ou un formateur** avant l'Epic 5 ? | A : **l'administrateur modifie directement**, chaque modification étant journalisée (il est la personne qui valide les corrections) ; les autres attendront l'Epic 5. B : personne ne modifie avant l'Epic 5 || ✅ A : l'administrateur modifie directement, journalisé |
| Q5 | **Formateurs venus de l'extérieur** : existent-ils ? | Si oui : leur donner un numéro de badge attribué par le CFDC dans le même format (par exemple une lettre réservée, `X..-..`) plutôt que changer la règle du badge | ✅ Non : tous les formateurs sont du personnel de l'AAN, avec un badge |
| Q6 | **Qui voit les documents de cours ?** | Le **formateur du module** et l'**administrateur** (`PRD.md` §6). Le coordonnateur et les chefs de service voient la **liste** des documents d'un module, mais ne les ouvrent pas. Dites-moi s'ils doivent pouvoir les ouvrir | ✅ Oui : formateur du module et administrateur ouvrent ; coordonnateur et chefs de service voient la liste |
| Q7 | **Taille maximale et formats** d'un document ? | **25 Mo** ; PDF, PowerPoint (`.ppt`, `.pptx`), Word (`.doc`, `.docx`), vérifiés par l'extension **et** le contenu du fichier | ✅ Oui : 25 Mo ; PDF, PowerPoint, Word, vérifiés par l'extension et le contenu |
| Q8 | **Documents sur le serveur de test**, perdus à chaque redémarrage | A : l'accepter (données fictives ; on vérifie le dépôt juste après l'envoi). B : un disque persistant Render (payant) || ✅ A : perte acceptée sur le serveur de test |
| Q9 | **Remplacer un document** (nouvelle version) ? | On dépose le nouveau ; l'ancien reste, marqué « remplacé » et toujours consultable par l'administrateur ; rien ne s'efface | ✅ Oui : l'ancienne version reste, « remplacée », ouverte par l'administrateur seulement |
| Q10 | **Un module peut-il exister sans formateur** (formateur pas encore choisi) ? | Oui : « Formateur à désigner » ; il n'apparaît alors dans aucun « Mes modules » | ✅ Oui : « Formateur à désigner » |
| Q11 | Corriger `PRD.md` §13 pour l'aligner sur §6 (emails pour l'accès en général) ? | Oui | ✅ Oui : `PRD.md` §13 corrigé le 2026-11-19 |

## Lot de user stories proposé

*Découpage et ordre validés par l'utilisateur le 2026-11-19.* Les numéros continuent ceux du projet (dernier : US-009).

| Ordre | User story | Périmètre en une ligne | Dépend de |
|---|---|---|---|
| 1 | US-010 Catalogue des formations | Domaines et sous-domaines (chargés au départ, l'administrateur en ajoute) ; enregistrer, lister et consulter une formation ; modification par l'administrateur ; écran « Formations » ; historique de la formation | — |
| 2 | US-011 Modules et formateurs | Ajouter des modules à une formation, désigner leur formateur (un compte au rôle formateur), page de la formation avec ses modules | US-010 |
| 3 | US-012 Documents de cours | Dépôt par l'administrateur (volume `documents`), formats et taille vérifiés, téléchargement protégé par les droits, écran « Documents de cours » | US-011 |
| 4 | US-013 « Mes modules » du formateur | Le formateur voit ses modules, leur formation et leurs documents, et rien d'autre | US-011 ; US-012 pour les documents |

**Ordre de construction à deux :** US-010 d'abord ; puis US-011 ; ensuite US-012 et US-013 en parallèle (US-013 affiche les documents dès que US-012 est fusionnée).

## Où sont allées les règles

*Clôture du 2026-11-23.*

| Règle | Document qui la porte désormais |
|---|---|
| Q1 — domaines et sous-domaines, liste de départ, gérés par l'administrateur | `SOLUTION_DESIGN.md` §6 ; `GLOSSARY.md` ; `functional-specs/ws-func-02-trainings-and-modules.md` § Domaines et sous-domaines |
| Q2 — intitulé unique, description facultative | `functional-specs/ws-func-02-trainings-and-modules.md` § Formations ; `PRD.md` §6 |
| Q3 — « formation importante » retirée, certificat sur demande | `PRD.md` §3 et §6 ; `GLOSSARY.md` |
| Q4 — l'administrateur corrige directement en attendant l'Epic 5 | `functional-specs/ws-func-02-trainings-and-modules.md` § Qui fait quoi |
| Q5 — tous les formateurs sont du personnel de l'AAN | `functional-specs/ws-func-02-trainings-and-modules.md` § Modules et formateurs |
| Q6 — qui ouvre les documents, qui voit la liste | `functional-specs/ws-func-02-trainings-and-modules.md` § Documents de cours ; `PRD.md` §6 |
| Q7 — 25 Mo, formats, contenu vérifié | `functional-specs/ws-func-02-trainings-and-modules.md` § Documents de cours ; `technical-specs/ws-tech-02-trainings-and-modules.md` |
| Q8 — fichiers perdus sur le serveur de test, accepté | `technical-specs/ws-tech-02-trainings-and-modules.md` § Stockage des fichiers |
| Q9 — remplacer garde l'ancienne version | `functional-specs/ws-func-02-trainings-and-modules.md` § Documents de cours |
| Q10 — module « Formateur à désigner » | `functional-specs/ws-func-02-trainings-and-modules.md` § Modules et formateurs |
| Q11 — emails pour l'accès en général | `PRD.md` §6 et §13 |
| Décisions des user stories (US-010 à US-013) | la paire WS-02 ; pour l'historique, la paire WS-05 |
