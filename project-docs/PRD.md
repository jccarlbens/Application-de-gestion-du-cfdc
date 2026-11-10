---
created: 2026-11-09T00:00:00Z
updated: 2026-11-10T15:52:09Z
---

# PRD.md — CFDC

**Répond à :** que construisons-nous, pour qui, pourquoi ?
**Dépend de :** rien — **c'est le premier document à remplir.** Le vocabulaire (`GLOSSARY.md`) se construit à partir de ce qui est décidé ici, et non l'inverse.

> **Statut : structure de départ.** Répondez vous-même aux questions de réflexion avant de demander à un agent de rédiger. Les sections marquées **Conditionnelle** sont des suppositions quant à leur pertinence — confirmez-les explicitement plutôt que de les accepter ou de les sauter en silence.
>
> **Essayez d'abord sans agent.** Ce document-ci en particulier mérite que vous y réfléchissiez avant d'ouvrir un agent — sur papier ou dans un brouillon. Un agent peut aider à formaliser une réponse que vous avez déjà ; s'il fournit la réponse à votre place, l'exercice ne construit pas la compétence qu'il vise : votre propre capacité à réfléchir et à planifier.

**En une ligne :** l'application CFDC retrace les formations que dispense l'Autorité Aéroportuaire Nationale (AAN) et aide à planifier leur calendrier.

---

## 1. Énoncé du produit

> 1. En une ou deux phrases, que fait réellement ce produit, et pour qui est-il ?
> 2. Quel problème réel résout-il ? En résout-il plus d'un, distinct, pour plus d'un public distinct ?
> 3. Pourquoi a-t-il besoin d'exister maintenant, pour cette personne, plutôt que d'être résolu autrement ?

**Ce que fait le produit.** L'application CFDC retrace les formations que dispense l'Autorité Aéroportuaire Nationale (AAN), à travers son Centre de Formation et de Développement des Compétences (CFDC). Pour chaque formation, elle conserve :
- la **présence** de chaque participant ;
- son **évaluation** ;
- son **attestation** : la preuve de sa participation, qui sert surtout au centre lui-même.

Les formations portent surtout sur la **sûreté et la sécurité** aéroportuaires, par exemple :
- la sensibilisation à la carte d'accès aéroportuaire ;
- la conduite sur le tarmac.

L'application joue deux rôles :
- une **base de données** des formations, à disposition des formateurs, des coordonnateurs et des chefs de service ;
- un **outil de planification** : programmer les sessions de formation et noter les formations demandées, afin d'affiner le calendrier.

**Pour qui.** Le personnel du CFDC : les formateurs, les coordonnateurs et les chefs de service du CFDC. Les participants, qu'ils soient internes à l'AAN ou externes (concessionnaires, etc.), n'utilisent pas l'application pour l'instant : ils sont enregistrés à la main par le personnel du CFDC.

**Le problème résolu.** Aujourd'hui, tout est géré sur papier. Cela pose trois problèmes :
- **les pertes** : un document égaré efface l'historique de formation ;
- **la fiabilité** : les informations sur papier sont difficiles à vérifier et peuvent être erronées ;
- **la dépendance envers une personne** : le suivi repose sur une seule personne ; sans elle, l'information n'est plus accessible.

**Pourquoi maintenant.** Le projet répond à une demande de la direction du CFDC, adjointe à la direction des ressources humaines de l'AAN.

## 2. Public

> 1. Qui va réellement utiliser ou croiser ceci, dans chacune de ses qualités distinctes — pas seulement l'utilisateur « principal » ?
> 2. Y a-t-il une logique derrière qui obtient l'accès et qui ne l'obtient pas ?
> 3. Quel public compte le plus si ses besoins entrent en conflit avec ceux d'un autre ?

**Les publics.** L'application connaît ces rôles :
- la **secrétaire**, qui enregistre les informations : formations, sessions, participants, présences, évaluations ;
- le **coordonnateur**, qui supervise et planifie les sessions de formation, et qui voit tout ;
- les **chefs de service du CFDC**, qui voient tout. Un chef de service extérieur au CFDC, par exemple celui du service qui demande une formation, **n'a pas accès** à l'application ;
- les **formateurs**, qui consultent les documents de cours (fichiers PDF, PowerPoint ou Word déposés par l'administrateur informatique) ;
- l'**administrateur informatique**, qui crée les comptes et effectue les modifications et les suppressions ;
- toute autre **personne autorisée**, qui peut consulter les informations.

Les participants, internes à l'AAN ou externes, ne sont pas des utilisateurs : ils sont enregistrés par la secrétaire (§1).

**Qui obtient l'accès.** Seules les personnes autorisées accèdent à l'application. Ce sont l'administrateur informatique et le coordonnateur qui donnent l'autorisation.

**Qui peut modifier ou supprimer.** Une information déjà enregistrée ne se modifie ou ne se supprime que **par l'intermédiaire de l'administrateur informatique**, y compris quand la demande vient de la secrétaire, du coordonnateur ou d'un chef de service. La personne fait une **demande de modification ou de suppression dans l'application**, et l'administrateur informatique la valide.

**En cas de conflit.** La **simplicité d'utilisation**, surtout pour la secrétaire qui saisit, passe avant le reste, par exemple avant le détail des bilans.

## 3. Scénario idéal de bout en bout

> 1. Décrivez, étape par étape, la meilleure expérience possible d'une personne réelle, du premier contact jusqu'au résultat qu'elle voulait.
> 2. Que faut-il qui soit vrai à chaque étape pour que ce scénario se produise réellement ?
> 3. À quel endroit de ce parcours l'expérience se briserait-elle aujourd'hui si rien de plus n'était construit ?

**Parcours d'une formation, de la demande à l'évaluation**
1. **La demande.** Le service concerné envoie une requête administrative écrite à la coordination du CFDC. La requête est enregistrée dans l'application, où la secrétaire et le coordonnateur peuvent l'ajuster.
2. **La planification.** Le coordonnateur fixe la date et la période de la session.
3. **L'horaire.** Les chefs de service du CFDC arrangent l'horaire.
4. **Les participants.** Le service demandeur fournit la liste de ses participants ; la secrétaire les enregistre.
5. **La présence.** Le jour de la formation, la présence est relevée par écrit, puis enregistrée dans l'application.
6. **L'évaluation.** Les participants sont évalués, généralement par un examen ou des questions. Le résultat est enregistré sous forme d'une **note**, accompagnée de **commentaires**. La note est **sur 100** ; la réussite demande au moins **la moyenne, soit 50/100**.
7. **L'attestation et le certificat.** Tous les participants présents reçoivent une **attestation**, qu'ils aient ou non la moyenne. Un **certificat** est délivré en plus, sur demande ou pour une formation que le **coordonnateur** décide d'estimer importante. Attestations et certificats sont **produits en dehors de l'application** ; l'application note leur **remise** et sa **date**.

**Où le parcours se brise aujourd'hui.** Aucune étape ne bloque en particulier. Le risque est réparti sur tout le parcours : ce sont les problèmes du papier décrits au §1, c'est-à-dire les pertes, le manque de fiabilité et la dépendance envers une personne.


## 4. Tâches à accomplir (Jobs to Be Done)

> 1. Qu'est-ce que l'utilisateur essaie d'accomplir, indépendamment de toute fonctionnalité que vous pourriez construire ?
> 2. Pour chaque tâche, que fait l'utilisateur aujourd'hui sans ce produit ?
> 3. Quelle tâche, si elle reste non résolue, rend le produit entier sans objet ?

| Rôle | Ce qu'il cherche à accomplir | Aujourd'hui |
|---|---|---|
| Secrétaire | Tenir à jour les formations à venir et leurs participants | Sur papier |
| Coordonnateur | Avoir une vue d'ensemble de l'unité | Sur papier |
| Chef de service du CFDC | *(à préciser)* | Sur papier |
| Formateur | *(à préciser)* | Sur papier |
| Administrateur informatique | *(à préciser)* | — |

**La tâche indispensable.** Que l'application soit **simple à utiliser**. Si elle ne l'est pas, le personnel reviendra au papier, et le produit n'aura plus d'objet.

## 5. Expérience produit par paliers *(Conditionnelle — à sauter s'il n'y a qu'un seul palier d'accès ou de capacité)*

> 1. Ce produit a-t-il plus d'un palier d'accès ou de capacité ? Combien, concrètement ?
> 2. Que peut voir ou faire chaque palier que celui du dessous ne peut pas ?
> 3. Une frontière de palier relève-t-elle ici de la confiance et de la sécurité, ou simplement de la richesse fonctionnelle ?

*(À écrire)*

## 6. Ce que le produit peut faire

> 1. Listez les capacités concrètes qu'un utilisateur peut invoquer, une par ligne, avec des verbes simples.
> 2. Pour chaque capacité, qu'est-ce qui la déclenche, et quelle en est la sortie réelle ?
> 3. Y a-t-il une capacité que tout le monde supposera existante mais qui n'est en fait pas prévue ? Énoncez-la explicitement comme hors périmètre dès maintenant.

*(À écrire)*

## 7. Ce que le produit ne doit jamais faire

> 1. Qu'est-ce qui serait activement nuisible, gênant ou dangereux si ce produit le faisait, ne serait-ce qu'une fois ?
> 2. Y a-t-il des sujets, des données ou des actions qui doivent toujours être redirigés vers un humain plutôt que traités automatiquement ?
> 3. Quel est le pire détournement plausible, et ce document dit-il ce qui se passe si quelqu'un l'essaie ?

*(À écrire)*

## 8. Voix et persona *(Conditionnelle — à sauter s'il n'y a aucune composante conversationnelle ou de voix de marque)*

> 1. Ce produit « parle »-t-il directement à quelqu'un — conversation, notifications, texte généré ? Si non, cette section ne s'applique pas.
> 2. Si oui, de qui est-ce la voix : celle d'une entreprise, d'un persona, la vôtre ?
> 3. Quel ton sonnerait faux pour ce produit, même en étant factuellement exact ?

*(À écrire)*

## 9. Modèle d'accès

> 1. Comment passe-t-on de « aucun accès » à « a l'accès » ? Qui l'approuve, si quelqu'un l'approuve ?
> 2. Qu'est-ce qui est stocké sur qui a l'accès, et qui peut le révoquer ?
> 3. Y a-t-il une différence entre « connecté » et « assez de confiance pour tout voir » ?

*(À écrire)*

## 10. Observabilité

> 1. Une fois en service, quelle est la première question à laquelle vous voudrez une réponse sur l'usage réel ?
> 2. De quoi auriez-vous besoin d'être alerté rapidement si quelque chose commençait à mal tourner ?
> 3. Qui regarde ces données, et à quelle fréquence ?

*(À écrire)*

## 11. Critères de succès

> 1. Comment saurez-vous, concrètement, que ce produit fonctionne comme prévu ?
> 2. Le succès se mesure-t-il à l'usage, à un résultat pour l'utilisateur, ou à votre propre jugement ?
> 3. Quelle est la plus petite version du « succès » qui vaudrait quand même d'avoir été livrée ?

*(À écrire)*

## 12. Critères d'échec et bloquants de mise en service

> 1. Que faut-il qui soit vrai avant que ceci soit autorisé à passer en service, de façon non négociable ?
> 2. Qu'est-ce qui vous ferait le retirer après le lancement ?
> 3. Y a-t-il ici une différence entre « pas encore parfait » et « réellement bloquant » ?

*(À écrire)*

## 13. Hors périmètre — V1

> 1. Que ne construisez-vous délibérément pas encore, même si c'est connexe ?
> 2. Que répondriez-vous à quelqu'un qui demande « pourquoi ça ne fait pas X » pour chaque élément exclu ?
> 3. Y a-t-il ici quelque chose qu'un lecteur novice supposerait probablement inclus ?

*(À écrire)*

## 14. Documents liés

> 1. De quels autres documents un nouveau lecteur a-t-il besoin, et dans quel ordre ?
> 2. Existe-t-il une carte canonique unique de tous les documents du projet, ou cette liste risque-t-elle de devenir une seconde copie qui dérive ?

*(À écrire)*

---
