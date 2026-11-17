---
created: 2026-11-17T00:00:00Z
updated: 2026-11-17T17:29:48Z
---

# WS-05 — Corrections et traçabilité : comportement

**Répond à :** que garde l'application de chaque modification, et qui peut la relire ?

> **Où commence cette spécification.** Elle ne couvre que **le journal des modifications**, construit par l'Epic 1 (US-003, et le panneau « Historique » de US-009). **Les demandes de correction** et leur validation par l'administrateur, le reste de WS-05, n'existent pas encore : elles arrivent avec l'Epic 5 et compléteront ce fichier.

**Implémentation :** `technical-specs/ws-tech-05-traceability.md`.

## Ce qui est gardé

- **Rien ne s'efface sans trace** (`PRD.md` §7). Une entrée de journal accompagne chaque création, modification et suppression d'une fiche. Elle indique :
  - la fiche visée ;
  - l'action ;
  - l'auteur ;
  - l'heure, en UTC ;
  - les valeurs **avant et après, en entier**.
- **La modification et sa trace s'enregistrent ensemble, ou pas du tout.**
- **L'auteur** est soit la personne connectée, soit un libellé :
  - « Ligne de commande (administrateur) » pour `create-admin`, `create-user` et `unblock-user` ;
  - « Titulaire du compte (lien de mot de passe) » quand la personne choisit son mot de passe par le lien ;
  - « Blocage automatique (5 échecs) ».
- **Les secrets n'y figurent jamais.** Un changement de mot de passe apparaît comme « [secret modifié] », sans aucune valeur ; les jetons des liens ne sont pas journalisés.
- **Personne ne peut modifier ni effacer le journal**, ni par l'application, ni directement dans la base.
- **Ce qui n'est pas dans ce journal :**
  - les **tentatives de connexion** ont leur propre registre, qui ne se modifie pas non plus ;
  - les sessions de connexion ne sont pas journalisées ;
  - le compte n'apparaît au journal que lorsqu'il est **bloqué**.
- **Les comptes créés avant US-003**, dont l'administrateur du serveur de test, n'ont pas de trace de leur création. C'était prévu et accepté : ce sont des données fictives.

## Qui relit quoi

- **L'historique d'une fiche** se voit dans l'ordre chronologique, par les rôles qui voient cette fiche. Aujourd'hui, seuls les comptes en ont un, visible par l'administrateur et le coordonnateur.
- **Les données personnelles** (NIF, CIN, téléphone…) restent en entier dans le journal, mais sont **masquées à la lecture** pour tout autre rôle que le coordonnateur et l'administrateur. Le mécanisme est prêt ; les champs concernés arrivent avec les participants (Epic 4).
- **Le panneau « Historique »** d'un compte (`/comptes/<numéro de badge>`) écrit chaque entrée en phrase : date, auteur, ce qui a changé.
  - Exemples : « Compte créé (X09-09) », « Rôle ajouté : Formateur », « Compte désactivé », « Mot de passe modifié ».
  - L'auteur est nommé (« Ada Admin (Z01-01) ») quand c'est une personne qu'on retrouve dans la liste des comptes ; sinon, son libellé s'affiche.
  - Un lien « Détails » montre l'avant et l'après de ce qui ne se traduit pas en phrase.
