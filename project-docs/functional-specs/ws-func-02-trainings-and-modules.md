---
created: 2026-11-20T00:00:00Z
updated: 2026-11-23T16:29:06Z
---

# WS-02 — Formations et modules : comportement

**Répond à :** que voit et que fait chacun, dans le catalogue des formations du CFDC ?
**Construit par :** Epic 2 (US-010 à US-013).
**Implémentation :** `technical-specs/ws-tech-02-trainings-and-modules.md`. **Journal :** `ws-func-05-traceability.md`.

## Qui fait quoi

| Action | Secrétaire | Coordonnateur | Chef de service | Formateur | Admin informatique | Direction |
|---|---|---|---|---|---|---|
| Voir le catalogue, les fiches, les modules et la liste des documents | ✅ | ✅ | ✅ | — | ✅ | ✅ |
| Enregistrer une formation, ajouter un module | ✅ | ✅ | ✅ | — | ✅ | — |
| Désigner le formateur d'un module « à désigner » | ✅ | ✅ | ✅ | — | ✅ | — |
| Modifier une formation ou un module, changer un formateur déjà désigné | — | — | — | — | ✅ | — |
| Ajouter ou renommer un domaine, un sous-domaine | — | — | — | — | ✅ | — |
| Déposer ou remplacer un document de cours | — | — | — | — | ✅ | — |
| Ouvrir un document en vigueur | — | — | — | ✅ *(ses modules)* | ✅ | — |
| Ouvrir une version remplacée | — | — | — | — | ✅ | — |
| « Mes modules » | — | — | — | ✅ | — | — |

**Rien ne se supprime** : ni domaine, ni formation, ni module, ni document. En attendant les demandes de correction (Epic 5), **seul l'administrateur modifie** ce qui est déjà enregistré, et chaque modification est journalisée.

Une personne qui a plusieurs rôles cumule leurs droits : par exemple, à la fois direction et formateur, elle voit le catalogue **et** « Mes modules ».

## Domaines et sous-domaines

- Le catalogue est classé sur **deux niveaux** : un domaine contient des sous-domaines, et chaque formation se range dans **un** sous-domaine.
- **Liste de départ**, chargée à l'installation :
  - **Sûreté-Sécurité** : Sensibilisation sur la carte d'accès, Conduite sur la rampe, Formation des policiers ;
  - **Accueil** : Protocole, Civilité.
- **L'administrateur ajoute ou renomme** un domaine ou un sous-domaine, depuis la page « Domaines et sous-domaines » (bouton sur l'écran « Formations », visible de lui seul).
  - Un nom déjà pris est refusé, sans tenir compte des majuscules. Le même nom de sous-domaine est permis dans deux domaines différents.
  - Chaque domaine et sous-domaine a son historique. Pour ceux de la liste de départ, il indique « Chargé à l'installation : pas d'entrée au journal ».

## Formations

- **Champs :**
  - **intitulé** : 200 caractères au plus ; **unique**, sans tenir compte des majuscules ni des espaces en trop, mais les accents comptent ;
  - **description** : facultative, 2 000 caractères au plus ;
  - **sous-domaine**.
- **L'écran « Formations »** regroupe les formations par domaine puis par sous-domaine, triées par nom, avec un filtre par domaine. Il n'y a pas de recherche : elle viendra avec l'Epic 6.
- **La fiche d'une formation** (`/formations/<numéro>`) montre son intitulé, son classement, sa description, ses modules et ses documents, et son **historique**.
  - Dans l'historique, chaque auteur est nommé « Prénom Nom (badge) », quel que soit le rôle du lecteur.
  - On y lit aussi les modules et les documents de la formation : « Module ajouté… », « Formateur désigné… », « Document déposé… ».
- **Il n'y a pas de « formation importante » :** la notion a été retirée du produit le 2026-11-19. Le certificat est remis sur demande, et sa remise sera notée avec l'Epic 4.

## Modules et formateurs

- **Un module** a un **titre** (200 caractères au plus, unique dans sa formation, sans tenir compte des majuscules), une **description** facultative et **un seul formateur**, ou « Formateur à désigner ».
- **Le formateur** est un compte **actif** qui a le rôle formateur. Tous les formateurs sont du personnel de l'AAN, avec un badge.
  - La liste proposée ne montre que leur nom et leur badge, jamais leurs données personnelles.
- **Les modules** s'affichent sur la fiche de la formation, dans l'ordre où ils ont été ajoutés. Une formation sans module affiche « Aucun module pour l'instant ».
- **Désigner ou changer un formateur :**
  - **désigner** le formateur d'un module « à désigner » est un complément, ouvert à ceux qui enregistrent les modules ;
  - **changer** un formateur déjà désigné est une modification, réservée à l'administrateur. Une secrétaire qui essaie est refusée : « Ce module a déjà un formateur : seul l'administrateur informatique peut le changer. »
- **Formateur parti :** un formateur dont le compte est désactivé reste sur ses modules, avec la mention « (compte désactivé) ». Un formateur qui n'a plus ce rôle porte la mention « (n'est plus formateur) ». L'administrateur désigne un remplaçant.

## Documents de cours

- **Dépôt :** l'administrateur dépose un document **dans un module**, sur la fiche de la formation.
  - Seuls les **PDF, Word (`.doc`, `.docx`) et PowerPoint (`.ppt`, `.pptx`)** de **25 Mo au plus** sont acceptés.
  - Le contenu du fichier doit correspondre à son extension ; un faux PDF est refusé. Un ancien `.doc` ou `.ppt` est reconnu comme document Office ancien, sans distinction entre Word et PowerPoint.
  - Les refus sont en français : « Format refusé… », « Le fichier dépasse 25 Mo. », « Le contenu du fichier ne correspond pas à son extension… ».
- **Remplacer** un document dépose une nouvelle version. L'ancienne passe dans « Versions remplacées », que seul l'administrateur ouvre.
- **Ce que chacun voit :**
  - tous ceux qui voient la fiche voient la liste des documents en vigueur de chaque module : nom, taille, date, déposé par ;
  - seuls le **formateur actuel du module** et l'administrateur **ouvrent** un document. Si le module change de formateur, l'ancien formateur perd l'accès.
- **Téléchargement :** le fichier garde son nom d'origine.
- **Page « Documents de cours »** (administrateur) : tous les documents en vigueur, par formation puis par module, avec un lien vers chaque fiche.
- **Sur le serveur de test** (Render gratuit), les fichiers disparaissent à chaque redémarrage ; la fiche du document reste. Le téléchargement répond alors « Le fichier de ce document est introuvable sur le serveur. »

## « Mes modules » (formateur)

- **La page** montre les modules dont la personne est le **formateur actuel**, regroupés par formation, triées par intitulé.
  - Pour chaque formation : l'intitulé, le classement et la description.
  - Pour chaque module : le titre, la description, et les documents en vigueur (nom, taille, date), qu'il télécharge.
- **Ce que le formateur ne voit pas :** les modules des autres formateurs, les modules « à désigner », les versions remplacées, ni le nom de la personne qui a déposé un document.
- **Sans module**, la page affiche « Aucun module ne vous est confié pour l'instant ».
- **Le formateur n'a pas accès au catalogue**, ni à la fiche d'une formation.
