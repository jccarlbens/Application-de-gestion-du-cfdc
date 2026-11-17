---
created: 2026-11-17T00:00:00Z
updated: 2026-11-17T17:29:48Z
---

# WS-01 — Comptes et accès : comportement

**Répond à :** que vit un membre du personnel du CFDC, de la création de son compte à sa déconnexion ?
**Construit par :** Epic 1 (US-002, US-004, US-007, US-009), clos le 2026-11-17. **Pas encore construit :** la double authentification par email ou SMS et le mot de passe oublié (Epic 7, US-005, US-006, US-008). Tant que l'Epic 7 n'est pas livré, la session s'ouvre directement après le mot de passe.
**Implémentation :** `technical-specs/ws-tech-01-accounts-and-access.md`. **Journal des actions sur les comptes :** `ws-func-05-traceability.md`.

## Les comptes

- **Pas d'inscription libre.** Seuls l'administrateur informatique et le coordonnateur créent des comptes.
  - L'administrateur peut donner n'importe quel rôle.
  - Le coordonnateur peut donner tous les rôles **sauf** « Administrateur informatique » : la case ne lui est même pas proposée.
  - Aucun autre rôle ne crée de compte.
- **Ce qu'on saisit :**
  - **numéro de badge** : une lettre majuscule, deux chiffres, un tiret, deux chiffres, par exemple `B07-42`. Il est saisi en minuscules ou en majuscules et enregistré en majuscules ; il est unique ;
  - **prénom et nom**, séparés ;
  - **email**, obligatoire et unique ;
  - **téléphone**, facultatif ;
  - **un ou plusieurs rôles** parmi les six : Secrétaire, Coordonnateur, Chef de service du CFDC, Formateur, Administrateur informatique, Direction du CFDC.
- **Le premier mot de passe.** Le compte est créé **sans mot de passe**. La personne reçoit par email un **lien** valable **48 heures**, à usage unique. Il ouvre la page « Choisir mon mot de passe », qui ne demande pas d'être connecté.
  - Un lien expiré ou déjà utilisé affiche « Ce lien n'est plus valable : il a expiré ou a déjà servi. ».
  - Si l'email ne part pas, **le compte n'est pas créé** : une erreur s'affiche et on recommence. Un compte sans mot de passe et sans lien ne pourrait plus servir, puisque rien ne se supprime.
- **Règle du mot de passe :** au moins 8 caractères, dont au moins un chiffre.
- **Seul l'administrateur informatique** change les rôles, désactive, réactive et débloque un compte, toujours après une confirmation à l'écran.
- **Le dernier administrateur actif** ne peut être ni désactivé ni privé de ce rôle : l'application ne reste jamais sans administrateur.
- **Un compte ne se supprime jamais.** Il se désactive, et son historique reste.
- **Le premier administrateur** se crée par la commande `create-admin`, une seule fois : elle refuse de s'exécuter si un administrateur existe déjà.
  - `create-user` crée d'autres comptes en ligne de commande.
  - `unblock-user` débloque un compte en ligne de commande.

## L'écran des comptes

Réservé à l'administrateur et au coordonnateur.

- **`/comptes`** : la liste triée par nom, avec le badge, le nom, les rôles et le statut. Le statut vaut « Actif », « Désactivé », « Bloqué » ou « En attente du mot de passe » (la personne n'a pas encore choisi son mot de passe). Sur téléphone, la liste s'affiche en cartes. Il n'y a pas de recherche : une dizaine de comptes suffit à trier par nom.
- **`/comptes/nouveau`** : le formulaire de création. Ensuite, la page affiche « Compte créé : un lien pour choisir le mot de passe a été envoyé à … ».
- **`/comptes/<numéro de badge>`** : la fiche du compte et son panneau « Historique », en phrases lisibles (`ws-func-05-traceability.md`).
  - L'administrateur y trouve les boutons « Modifier les rôles », « Désactiver » ou « Réactiver », et « Débloquer » pour un compte bloqué.
  - Le coordonnateur ne voit aucun de ces boutons.
- **Les refus du serveur** s'affichent en français : badge ou email déjà pris, dernier administrateur…

## La connexion

- **On se connecte avec son numéro de badge et son mot de passe.**
- **Des identifiants faux** affichent toujours « Numéro de badge ou mot de passe incorrect. », sans dire lequel des deux est faux. Un numéro de badge inconnu prend le même temps de réponse qu'un mot de passe faux.
- **Un compte bloqué ou désactivé** n'est annoncé comme tel qu'à la personne qui a donné le bon mot de passe.
- **Blocage :** au **5e échec consécutif**, le compte est bloqué.
  - Seul l'administrateur le débloque, depuis la fiche du compte ou par `unblock-user`.
  - Une connexion réussie ou un déblocage remettent le compteur à zéro.
  - Il n'y a **pas de limite par adresse IP**. C'est un risque accepté pour la V1 (`NFR.md` § Risques).
- **La session expire après 15 minutes sans activité.** Chaque action la prolonge. Une session expirée ramène à l'écran de connexion avec « Votre session a expiré, reconnectez-vous. ».
- **« Se déconnecter »** ferme la session tout de suite.
- **Désactiver ou bloquer un compte** ferme immédiatement toutes ses sessions ouvertes.

## Les droits et les menus

- **Le serveur décide.** Chaque action est refusée (`403` « Votre rôle ne permet pas cette action. ») si aucun des rôles de la personne ne l'autorise, même quand l'interface a été contournée. Masquer un menu ne suffit jamais.
- **Accueil :**
  - « Connecté : Prénom Nom (badge) » ;
  - les rôles en français ;
  - des raccourcis vers les menus de la personne.
- **Menus.** Une personne ne voit que les menus de ses rôles ; avec plusieurs rôles, elle voit l'union de leurs menus.
  - Sur ordinateur, les menus forment une barre à gauche ; sur téléphone, ils s'ouvrent avec un bouton « Menu ».
  - Un menu dont l'écran n'existe pas encore mène à « Bientôt disponible ».
  - Une page qu'on n'a pas le droit de voir affiche « Vous n'avez pas accès à cette page. ».

| Menu | Secrétaire | Coordonnateur | Chef de service | Formateur | Admin informatique | Direction |
|---|---|---|---|---|---|---|
| Formations | ✅ | ✅ | ✅ | — | ✅ | ✅ |
| Mes modules | — | — | — | ✅ | — | — |
| Demandes de formation | ✅ | ✅ | ✅ | — | ✅ | ✅ |
| Sessions et calendrier | ✅ | ✅ | ✅ | — | ✅ | ✅ |
| Participants | ✅ | ✅ | ✅ | — | ✅ | ✅ |
| Documents de cours | — | — | — | — | ✅ | — |
| Demandes de correction | — | — | — | — | ✅ | — |
| Comptes | — | ✅ | — | — | ✅ | — |
| Vue d'ensemble | — | ✅ | ✅ | — | ✅ | ✅ |

*Tableau validé le 2026-11-17 (US-007). Un Epic qui ajoute un écran le branche sur son menu ; s'il change un droit, il change ce tableau.*

## Le serveur de test

Il tourne sur Render, avec la base sur Neon, et **ne reçoit que des données fictives** : aucun vrai participant, NIF ou CIN. Les emails y partent par Brevo. Les vraies données n'arriveront que sur les serveurs de l'AAN, après l'Epic 7.
