---
created: 2026-09-08T17:38:40Z
updated: 2026-11-09T17:14:13Z
---

> **Premier apprentissage :** 2026-08-13 18:04:50
> **Dernière mise à jour :** 2026-08-13 18:10:19

## Contexte

Annexe de `01-documentation-structure-template.md` : ce fichier-là enseigne la forme d'ensemble (quel document répond à quelle question, dans quel ordre, physiquement disposé comment) ; celui-ci décompose chacun de ces documents en ses sections réelles et donne 3 à 5 questions de remue-méninges par section, pour que celui qui démarre un nouveau projet y réfléchisse — seul ou en en discutant avec un agent — avant ou pendant la rédaction de cette section.

L'usage visé : une personne qui démarre un nouveau projet lit les questions d'une section, y réfléchit ou en discute avec un agent, et arrive à la session avec assez de clarté pour bien remplir cette section, au lieu de fixer un gabarit vide ou de demander à un agent d'inventer le contenu à sa place. Les questions sont l'échafaudage ; les réponses doivent être celles de la personne.

`.claude/skills/*/SKILL.md` est délibérément exclu : une compétence est une procédure (la façon dont une tâche récurrente s'exécute), et non quelque chose dont on atteint le contenu par la réflexion.

Également absent à dessein : des questions de réflexion pour un document de stratégie de test, parce qu'aucun tel document n'existe dans le tableau de `01` pour être décomposé — quel ou quels cadres de test employer et comment les tests fonctionneront réellement est laissé à émerger quand il y a du code réel à tester, et non décidé de façon spéculative d'avance. Voir la note correspondante de `01-documentation-structure-template.md` pour l'endroit où cette décision atterrirait si un projet atteignait le point d'avoir besoin de l'écrire.

## Comment cela a été appris

**Le déclencheur :** après que `01` a eu une arborescence physique générique, la couche suivante a été demandée : pour chaque document du tableau de dépendances de `01`, lister ses sections réelles, trier chacune entre « générique — à réutiliser telle quelle » et « propre à ce projet — en voici la version généralisée », et attacher 3 à 5 questions de réflexion par section. Un soin particulier a été demandé sur `PRD.md` en particulier, puisqu'il a tendance à comporter le plus de sections qui n'ont de sens que pour une sorte de produit bien particulière.

**Le chemin :** les en-têtes de section réels ont été extraits de chaque document vivant d'un projet en fonctionnement (`GLOSSARY.md`, `PRD.md`, `NFR.md`, `SOLUTION_DESIGN.md`, `PLAN.md`, `project-docs/execution/EPIC_EXECUTION.md`, `project-docs/functional-specs/`, `project-docs/technical-specs/`, une user story `US-NNN.md`, `project-docs/PROJECT_WORKFLOW.md`, `CLAUDE.md`) plutôt que reconstitués de mémoire, puisqu'une liste de sections obsolète ici serait pire que pas de liste du tout.

**Points de vigilance :**
- Deux documents n'entrent pas du tout dans la forme « liste de sections fixes », et sont traités différemment ci-dessous plutôt que forcés dedans : `project-docs/execution/EPIC_EXECUTION.md` est un suivi dérivé, non rédigé par réflexion — il se remplit automatiquement à mesure que les Epics de `PLAN.md` sont travaillés. `project-docs/functional-specs/` et `project-docs/technical-specs/` n'ont aucun gabarit figé — leurs propres README le confirment — les sections se décident par Workstream, selon ce qui a réellement besoin d'être documenté une fois qu'un comportement ou une implémentation réels existent, créées de façon incrémentale, jamais d'avance.
- Certaines sections sont véritablement conditionnelles, et pas seulement « généralisables » — la section Voix et persona de `PRD.md`, par exemple, ne s'applique que si le produit a une composante conversationnelle ou de voix de marque. Marquer une section « sans objet, à sauter » est en soi une catégorie utile, distincte de « générique, à garder » et de « propre, à généraliser ».
- `NFR.md` n'a presque eu besoin d'aucune généralisation — ISO 25010 est déjà un modèle de qualité indépendant du projet. Cette asymétrie (le NFR change à peine, le PRD change beaucoup) vaut en soi d'être remarquée : plus un document décrit *ce qu'est ce produit précis*, moins ses sections exactes sont transposables ; plus il décrit *un niveau de qualité ou un processus*, plus il est transposable.

## La règle

Chaque entrée ci-dessous : le document, son objet (d'après le tableau de `01`), ses sections marquées **Générique** (réutilisez l'intitulé tel quel), **À généraliser** (un intitulé trop propre à un produit — une version réutilisable est donnée), ou **Conditionnelle** (à inclure seulement si cela s'applique à votre produit) — suivies des questions de réflexion par section générique ou généralisée.

---

### 1. `GLOSSARY.md` — que veut dire ce terme ?

Les en-têtes de catégorie d'un glossaire sont façonnés par le produit qu'il décrit — ne copiez pas les *noms* de catégorie d'un produit à l'autre, copiez le motif sous-jacent :

| Catégorie (généralisée) | Exemple d'instanciation |
|---|---|
| **Acteurs et rôles** — qui ou quoi interagit avec le système en une qualité distincte | Agents, profils de visiteur, modes de fonctionnement |
| **Composants du système** — les pièces exécutées ou déployées indépendamment | Frontends, services backend |
| **Magasins de données** — où l'information persiste réellement | Bases de données, caches, stockages de fichiers |
| **Vocabulaire du domaine** — les termes de processus ou de contenu qu'une personne extérieure lirait de travers | Types de contenu, processus, termes d'authentification et d'accès |
| **Workstream, Epic et Milestone** — Générique, à réutiliser mot pour mot | identique |
| **Documents du projet** — Générique, motif de simple renvoi | identique |

**Acteurs et rôles**
1. Qui ou quoi touche ce système, et chacun a-t-il besoin de capacités, d'accès ou de niveaux de confiance différents ?
2. Y a-t-il un mot (comme « utilisateur » ou « agent ») qui pourrait désigner deux choses différentes selon le contexte, ici ? Faut-il le scinder en deux termes ?
3. Y a-t-il des modes ou des intentions distincts dans lesquels un même acteur peut se trouver, et qui méritent d'être nommés séparément ?

**Composants du système**
1. Quelles sont les pièces exécutables ou déployables indépendamment de ce système ?
2. Deux composants portent-ils des noms assez proches pour être confondus ? Qu'est-ce qui distingue chacun en une phrase ?
3. Y a-t-il un découpage naturel qui mérite d'être nommé comme catégorie (public contre privé, permanent contre à la demande) ?

**Magasins de données**
1. Où l'information persiste-t-elle réellement, et combien de magasins distincts y a-t-il ?
2. Un magasin détient-il plus d'une sorte de donnée qui mériterait d'être nommée séparément ?
3. Quel magasin, s'il était perdu, causerait le plus de dommages ?

**Vocabulaire du domaine**
1. Quels noms récurrents ou noms de processus une personne extérieure interpréterait-elle de travers sans définition ?
2. Quels termes reviennent sans arrêt dans les conversations sur ce projet sans être évidents à partir du mot seul ?
3. Y a-t-il un terme emprunté à un champ plus large (par exemple « epic », « jeton ») qui signifie ici quelque chose de plus étroit ?

**Workstream, Epic et Milestone**
1. Ce projet a-t-il véritablement besoin des trois axes — domaine fonctionnel / étape séquentielle bornée dans le temps / point de contrôle livrable — ou est-il assez petit pour que deux d'entre eux se confondent en un seul ?
2. Quels sont les Workstreams réels de ce projet (ses domaines fonctionnels), indépendamment du moment où chacun sera travaillé ?

**Documents du projet**
1. Quel document unique est la carte canonique de tous les autres documents, pour que celui-ci reste un renvoi et jamais une seconde copie ?

---

### 2. `PRD.md` — que construisons-nous, pour qui, pourquoi ?

La section qui mérite le plus d'être repensée à chaque projet. Un produit d'agent conversationnel, une application de suivi de données et un tableau de bord CRUD ont besoin de sous-ensembles différents — généralisez ou marquez conditionnel en conséquence :

| Section | Traitement |
|---|---|
| 1. Énoncé du produit | Générique |
| 2. Public | Générique |
| 3. Scénario idéal de bout en bout | Générique |
| 4. Tâches à accomplir | Générique |
| 5. Expérience produit par paliers | Générique (quel que soit le nombre réel de paliers d'accès ou de capacité — il pourrait n'y en avoir qu'un, ou plusieurs) |
| 6. Ce que le produit peut faire | Générique |
| 7. Ce que le produit ne doit jamais faire | Générique — précieux pour tout produit comportant des composantes automatisées ou des données sensibles |
| 8. Voix et persona | **Conditionnelle** — seulement s'il y a une composante conversationnelle ou de voix de marque ; à sauter entièrement sinon |
| 9. Modèle d'accès | Générique |
| 10. Observabilité | Générique |
| 11. Critères de succès | Générique |
| 12. Critères d'échec et bloquants de mise en service | Générique |
| 13. Hors périmètre — V1 | Générique |
| 14. Documents liés | Générique |

**Énoncé du produit**
1. En une ou deux phrases, que fait réellement ce produit, et pour qui est-il ?
2. Quel problème réel cela résout-il ? Cela résout-il plus d'un problème distinct pour plus d'un public distinct ?
3. Pourquoi cela a-t-il besoin d'exister maintenant, pour cette personne, plutôt que d'être résolu autrement ?

**Public**
1. Qui va réellement utiliser ou croiser ceci, dans chacune de ses qualités distinctes, et non seulement l'utilisateur « principal » ?
2. Y a-t-il une philosophie derrière qui obtient l'accès et qui ne l'obtient pas ?
3. Quel public compte le plus si ses besoins entrent en conflit avec ceux d'un autre public ?

**Scénario idéal de bout en bout**
1. Parcourez, étape par étape, la meilleure expérience possible d'une personne réelle, du premier contact jusqu'au résultat qu'elle voulait.
2. Que faut-il qui soit vrai à chaque étape pour que ce scénario se produise réellement ?
3. À quel endroit de ce parcours l'expérience se briserait-elle aujourd'hui si rien de plus n'était construit ?

**Tâches à accomplir**
1. Qu'est-ce que l'utilisateur essaie d'accomplir, indépendamment de toute fonctionnalité que vous pourriez construire ?
2. Pour chaque tâche, que fait l'utilisateur aujourd'hui sans ce produit ?
3. Quelle tâche, si elle reste non résolue, rend le produit entier sans objet ?

**Expérience produit par paliers**
1. Ce produit a-t-il plus d'un palier d'accès ou de capacité ? Combien, concrètement ?
2. Que peut voir ou faire chaque palier que celui du dessous ne peut pas ?
3. Une frontière de palier relève-t-elle ici de la confiance et de la sécurité, ou simplement de la richesse fonctionnelle ?

**Ce que le produit peut faire**
1. Listez les capacités concrètes qu'un utilisateur peut invoquer, une par ligne, avec des verbes simples.
2. Pour chaque capacité, qu'est-ce qui la déclenche, et quelle en est la sortie réelle ?
3. Y a-t-il une capacité que tout le monde supposera existante et qui n'est en fait pas prévue ? Elle vaut d'être énoncée dès maintenant comme explicitement hors périmètre.

**Ce que le produit ne doit jamais faire**
1. Qu'est-ce qui serait activement nuisible, gênant ou dangereux si ce produit le faisait, ne serait-ce qu'une fois ?
2. Y a-t-il des sujets, des données ou des actions qui doivent toujours être redirigés vers un humain plutôt que traités automatiquement ?
3. Quel est le pire détournement plausible, et ce document dit-il ce qui se passe quand quelqu'un l'essaie ?

**Voix et persona** *(à sauter si non applicable)*
1. Ce produit « parle »-t-il directement à quelqu'un — conversation, notifications, texte généré ? Si non, cette section ne s'applique pas.
2. Si oui, de qui est-ce la voix : celle d'une entreprise, d'un persona, du fondateur lui-même ?
3. Quel ton sonnerait faux pour ce produit, même en étant factuellement exact ?

**Modèle d'accès**
1. Comment passe-t-on de « aucun accès » à « a l'accès » ? Qui l'approuve, si quelqu'un l'approuve ?
2. Qu'est-ce qui est stocké sur qui a l'accès, et qui peut le révoquer ?
3. Y a-t-il une différence entre « connecté » et « assez de confiance pour tout voir » ?

**Observabilité**
1. Une fois en service, quelle est la première question à laquelle vous voudrez une réponse sur la façon dont c'est réellement employé ?
2. Que faudrait-il que vous remarquiez vite si quelque chose commençait à mal tourner ?
3. Qui regarde ces données, et à quelle fréquence ?

**Critères de succès**
1. Comment saurez-vous, concrètement, que ce produit fonctionne comme prévu ?
2. Le succès se mesure-t-il à l'usage, à un résultat pour l'utilisateur, ou à votre propre jugement ?
3. Quelle est la plus petite version du « succès » qui vaudrait quand même la peine d'avoir été livrée ?

**Critères d'échec et bloquants de mise en service**
1. Que faut-il qui soit vrai avant que ceci soit autorisé à passer en service, de façon non négociable ?
2. Qu'est-ce qui vous ferait le retirer après le lancement ?
3. Y a-t-il ici une différence entre « pas encore parfait » et « réellement bloquant » ?

**Hors périmètre — V1**
1. Que ne construisez-vous délibérément pas encore, même si c'est connexe ?
2. Que répondriez-vous à quelqu'un qui demande « pourquoi ça ne fait pas X » à propos de chaque élément exclu ?
3. Y a-t-il ici une exclusion qu'un lecteur novice supposerait probablement incluse ?

**Documents liés**
1. De quels autres documents un nouveau lecteur a-t-il besoin, et dans quel ordre ?
2. Existe-t-il une carte canonique unique de tous les documents du projet, ou cette liste risque-t-elle de devenir une seconde copie qui dérive ?

---

### 3. `NFR.md` — quel niveau de qualité doit-il atteindre ?

Toutes génériques — ISO 25010 est un modèle de qualité indépendant du projet. La seule modification propre à chaque projet est de savoir quel régime réglementaire s'applique réellement dans Conformité et aspects juridiques.

**Performance**
1. Quel temps de réponse donnerait à un utilisateur réel l'impression que c'est cassé ?
2. Y a-t-il un moment de charge de pointe connu (un lancement, une heure précise) ?
3. Que mesure-t-on réellement — le chargement d'une page, la latence d'une API, autre chose ?

**Fiabilité et disponibilité**
1. Que signifie « en panne » pour ce produit, précisément ?
2. Une indisponibilité est-elle acceptable, et quand ?
3. Quel est le plan si une dépendance dont ceci dépend tombe ?

**Capacité de montée en charge**
1. Que se passe-t-il si l'usage est multiplié par dix du jour au lendemain ?
2. Quelle ressource s'épuise la première ?
3. La montée en charge est-elle ici un risque réel à court terme, ou une hypothèse pour la V1 ?

**Sécurité**
1. Quelle est la chose la plus sensible que ce système détient ?
2. Qui ne doit jamais pouvoir y accéder ?
3. Quel est le pire scénario de compromission, et est-il survivable ?

**Utilisabilité et accessibilité**
1. Qui pourrait avoir du mal à utiliser ceci tel que conçu — appareil, langue, capacités ?
2. Y a-t-il une norme d'accessibilité minimale visée ?
3. Quelle est la tâche la plus simple qu'un utilisateur novice doit pouvoir accomplir sans aide ?

**Compatibilité**
1. Sur quels environnements (navigateurs, appareils, systèmes d'exploitation) ceci doit-il réellement fonctionner ?
2. Y a-t-il un environnement explicitement non pris en charge ?
3. Faut-il interopérer avec un système existant ?

**Conformité et aspects juridiques**
1. Quelle réglementation s'applique à ces données ou à ce public ?
2. Quel consentement ou quelle information est légalement exigé avant de collecter des données ?
3. Qui est responsable si cela tourne mal ?

**Maintenabilité**
1. À quel point est-il facile, pour une personne future — y compris vous-même plus tard — de modifier ceci sans danger ?
2. Quel est le plan pour maintenir la documentation en phase avec le code ?
3. Y a-t-il une suite de tests, et que couvre-t-elle réellement ?

**Portabilité**
1. Ceci pourrait-il déménager chez un autre hébergeur ou fournisseur sans réécriture complète ?
2. Y a-t-il quelque chose de codé en dur pour un fournisseur unique qui ne devrait pas l'être ?

**Observabilité et supervision**
1. De quoi voudriez-vous être alerté immédiatement en cas de panne ?
2. Qu'est-ce qui est journalisé aujourd'hui, par rapport à ce qui devrait l'être ?
3. Qui surveille cela réellement ?

**Reprise après sinistre et sauvegardes**
1. Quel est le pire scénario de perte de données, et comment vous en remettriez-vous ?
2. À quelle fréquence les données sont-elles sauvegardées, et une restauration a-t-elle déjà été réellement testée ?
3. Quelle perte de données (RPO) et quelle indisponibilité (RTO) sont acceptables ?

**Risques et mesures d'atténuation**
1. Qu'est-ce qui risque le plus de mal tourner avant la livraison ?
2. Pour chaque risque, quel est le plan s'il se produit malgré tout ?
3. Quel risque, s'il se réalisait, serait le plus difficile à surmonter ?

**Dépendances**
1. De quels services externes, bibliothèques ou personnes ceci dépend-il pour fonctionner ?
2. Que se passe-t-il si l'un devient indisponible ou change son API ?
3. Y a-t-il parmi eux un point de défaillance unique ?

---

### 4. `SOLUTION_DESIGN.md` — comment est-ce construit, et en quels Workstreams cela se décompose-t-il ?

| Section | Traitement |
|---|---|
| 1. Objet et périmètre | Générique |
| 2. Workstreams | Générique — la définition canonique de l'identifiant de Workstream |
| 3. Vue d'ensemble du système | Générique |
| 4. Carte des composants (services et ports, diagramme, liste d'outils) | Motif générique ; le contenu précis est toujours propre au produit |
| 5. Pile technique | Générique |
| 6. Couche de données | Motif générique ; la répartition précise des magasins est propre au produit |
| 7. Flux d'authentification et d'autorisation | **Conditionnelle** — seulement si le produit a un contrôle d'accès |
| 8. Architecture temps réel ou interactive | **Conditionnelle** — seulement s'il y a une couche en direct ou en flux |
| 9-10. Boucle de mise à jour ou de retour automatisée | **Conditionnelle** — seulement si le contenu ou le comportement se met à jour automatiquement plutôt que par édition manuelle |
| 11. Vue d'ensemble du déploiement | Générique |
| 12. Hypothèses | Générique |
| 13. Hors périmètre | Générique |
| 14. Registres de décision d'architecture | Générique — réutilisez le motif du tableau d'ADR mot pour mot |
| 15. Questions ouvertes | Générique |

**Objet et périmètre**
1. De quoi ce document est-il responsable de décider, qu'aucun autre document ne décide ?
2. Qu'est-ce qui est explicitement en dehors de l'autorité de ce document (par exemple, les décisions produit appartiennent au PRD) ?

**Workstreams**
1. Quels sont les domaines fonctionnels indépendants de ce système, indépendamment de l'ordre de construction ?
2. Deux Workstreams pourraient-ils un jour être travaillés par des personnes différentes en même temps sans se gêner ?
3. Y a-t-il un Workstream caché à l'intérieur d'un autre qui mériterait son propre identifiant ?

**Vue d'ensemble du système**
1. En quelques phrases, comment les pièces principales s'articulent-elles de bout en bout ?
2. Quel est le diagramme ou le flux unique qui expliquerait cela le plus vite à un nouvel ingénieur ?

**Carte des composants**
1. Quels sont les composants réellement exécutables ou déployables, et qu'est-ce que chacun possède ?
2. Quels ports, quelles URL, quels points d'entrée chacun expose-t-il ?
3. Y a-t-il ici un composant qui est en réalité deux composants déguisés en un seul ?

**Pile technique**
1. Quelle est la pile pour chaque partie majeure du système, et pourquoi ce choix précisément ?
2. Y a-t-il une pièce de la pile qui est un espace réservé ou une supposition plutôt qu'une vraie décision à ce stade ?

**Couche de données**
1. Où vit réellement chaque sorte de donnée, et sous quelle forme ?
2. Quel magasin est la source de vérité si deux magasins pouvaient se contredire ?
3. Quel est le schéma ou le contrat, assez précisément pour que deux implémentations ne dérivent pas ?

**Flux d'authentification et d'autorisation** *(à sauter s'il n'y a aucun contrôle d'accès)*
1. Étape par étape, comment passe-t-on d'anonyme à authentifié, puis à autorisé pour une action précise ?
2. Qu'est-ce qui est émis (un jeton, une session, une clé), et que prouve-t-il réellement ?

**Architecture temps réel ou interactive** *(à sauter si rien n'est en direct ni en flux)*
1. Qu'est-ce qui doit se passer en temps réel, par rapport à ce qui peut rester en requête/réponse ?
2. Quel est le repli si le canal temps réel tombe au milieu d'une interaction ?

**Boucle de mise à jour ou de retour automatisée** *(à sauter si le contenu ne change que par édition manuelle)*
1. Quelque chose dans ce système se met-il à jour tout seul en fonction de l'usage ou de nouvelles données ? Qu'est-ce qui le déclenche ?
2. Qui relit un changement automatisé avant sa mise en service, si quelqu'un le fait ?
3. Quelle est la pire chose qu'une boucle de mise à jour automatisée pourrait faire si on la laissait sans contrôle ?

**Vue d'ensemble du déploiement**
1. Où ceci tourne-t-il réellement aujourd'hui, et où tournera-t-il au lancement ?
2. Quel est le chemin entre un changement local et sa mise en service ?
3. Y a-t-il une étape de CI/CD, et qu'est-ce qu'elle conditionne réellement ?

**Hypothèses**
1. Qu'est-ce que cette conception suppose vrai sans que cela ait encore été réellement vérifié ?
2. Quelle hypothèse, si elle était fausse, imposerait une refonte plutôt qu'un correctif ?

**Hors périmètre**
1. Qu'est-ce qui est architecturalement exclu de cette version, et pourquoi ?
2. Y a-t-il ici une exclusion qu'un Workstream ultérieur devra revisiter ?

**Registres de décision d'architecture**
1. Qu'a-t-on décidé qui aurait plausiblement pu aller dans l'autre sens ?
2. Pourquoi l'autre option a-t-elle été rejetée, assez précisément pour que personne ne la repropose sans le savoir ?
3. Cette décision est-elle toujours d'actualité, ou a-t-elle besoin d'une entrée `Dépréciée` avec une raison ?

**Questions ouvertes**
1. Qu'est-ce qui est véritablement non résolu à l'instant, qui ne devrait pas bloquer le démarrage, mais ne devrait pas être oublié non plus ?
2. Qui ou quoi résoudrait chaque question ouverte, et quand ?

---

### 5. `PLAN.md` — dans quel ordre, regroupé en quels Epics ?

Toutes les sections sont génériques (motifs de séquencement et de priorisation, et non du contenu propre au produit).

**Vue d'ensemble des Epics**
1. Dans quel ordre les domaines fonctionnels seront-ils réellement travaillés, et pourquoi cet ordre ?
2. Un Epic est-il bloqué par l'achèvement d'un autre ?
3. Deux Epics pourraient-ils véritablement avancer en parallèle, ou le séquentiel est-il réellement nécessaire ici — et pourquoi ?

**Tâches à accomplir — référence**
1. Chaque tâche à accomplir correspond-elle à exactement un Epic, ou l'une d'elles s'étend-elle sur plusieurs ?
2. Ce tableau n'est-il encore qu'un renvoi vers les véritables définitions du PRD, ou du contenu a-t-il commencé à s'y dupliquer ?

**Priorisation MoSCoW**
1. Pour chaque tâche à accomplir, qu'est-ce qui est vraiment indispensable (*Must*) par opposition à souhaitable (*Should*), possible (*Could*) ou exclu (*Won't*) pour la V1 ?
2. Quel est le coût de s'être trompé sur quelque chose marqué indispensable et qui se révèle inutile ?
3. Y a-t-il quelque chose marqué exclu dont on risque quand même de vous parler — et qui vaut d'être énoncé explicitement plutôt qu'abandonné en silence ?

**Sections de détail par Epic**
1. Que livre cet Epic que le précédent ne livrait pas ?
2. Quel ou quels Workstreams touche-t-il principalement ?
3. Quel est l'objectif en une phrase qu'une partie prenante pourrait répéter correctement ?

**Prochaines étapes immédiates**
1. Quelle est la toute prochaine action concrète, et non une reformulation de la feuille de route entière ?
2. Cette section risque-t-elle de devenir vite obsolète — le statut au quotidien devrait-il plutôt vivre dans un suivi dédié ?

---

### 6. `project-docs/execution/EPIC_EXECUTION.md` — quel est le statut de chaque user story, à l'instant ?

Non rédigé par réflexion — c'est un suivi dérivé, rempli automatiquement à mesure que les Epics de `PLAN.md` sont travaillés et que les user stories se closent. Aucun contenu à imaginer ; seulement un contrôle de processus :

1. Ce tableau est-il encore vrai à l'instant, ou le statut d'une user story a-t-il changé sans que ce fichier soit mis à jour ?
2. Chaque Epic de `PLAN.md` a-t-il une section correspondante ici, dans le même ordre ?

---

### 7. `project-docs/functional-specs/` et `project-docs/technical-specs/` — que fait réellement un Workstream livré / comment est-il réellement construit ?

Aucun gabarit de sections figé n'existe pour l'un ni pour l'autre — confirmé par le README de chacun des deux dossiers. Les sections se décident par Workstream, de façon incrémentale, une fois qu'un comportement ou une implémentation réels existent à documenter ; les écrire d'avance serait de la spéculation. Employez ces questions pour décider *si une section est nécessaire du tout*, et non pour remplir une liste figée :

**Spécification fonctionnelle (le comportement)**
1. Qu'est-ce qu'un utilisateur ou un système appelant observe maintenant, qu'il ne pouvait pas observer avant que ce Workstream existe ?
2. Quels sont les cas limites ou les conditions de refus qu'une personne construisant contre ceci doit connaître ?
3. Y a-t-il ici une règle qui n'est pas évidente à la lecture du code — une règle métier, une frontière de confidentialité, une exigence d'ordonnancement ?

**Spécification technique (l'implémentation)**
1. Que devrait savoir un nouvel ingénieur pour modifier ceci sans danger, sans casser un invariant ?
2. Quel est le contrat de données, le schéma ou la règle de nommage exacts, assez précis pour que deux implémentations ne s'éloignent pas l'une de l'autre ?
3. Quelle décision prise ici était assez peu évidente pour que quelqu'un puisse plus tard la « corriger » en revenant à la mauvaise option ?

**La question qui gouverne les deux :** une user story de ce Workstream s'est-elle réellement close ? Si non, il n'y a rien de réel à documenter — attendez.

---

### 8. `project-docs/execution/epic-NNN-*/US-NNN.md` — qu'a-t-on précisément demandé et accepté pour une unité de travail ?

Déjà entièrement générique (le format de user story partagé) — le seul lien propre au projet est que le « rôle » doit être un vrai rôle de *votre* glossaire, et non celui d'un projet d'exemple.

**En tant que / Je veux / Afin de**
1. Qui veut cela précisément — quel rôle nommé du glossaire, et non juste « un utilisateur » ?
2. Que veut-il pouvoir faire, en une phrase ?
3. Pourquoi ce résultat compte-t-il pour lui, et pas seulement pour vous qui construisez ?

**Contexte**
1. Qu'est-ce qui existe déjà et sur quoi ceci s'appuie ?
2. Qu'est-ce qui ne doit explicitement *pas* être supposé déjà fait ?

**Critères d'acceptation**
1. Quel est le plus petit énoncé testable qui soit sans ambiguïté vrai ou faux une fois ceci terminé ?
2. Y a-t-il ici un critère qui est en réalité une tâche déguisée — une étape d'implémentation, et non un résultat observable ?

**Hors périmètre**
1. Qu'est-ce qui est adjacent à cette user story et qu'un lecteur pourrait supposer inclus, sans l'être ?

**Tâches**
1. Quelle est la prochaine action concrète, dans un ordre qu'on pourrait réellement suivre du début à la fin ?

**Définition du terminé**
1. Que vérifie réellement, de ses propres yeux, la personne qui a demandé ceci pour l'accepter ?

**Notes de réalisation**
1. Qu'est-ce qui a changé entre ce qui était prévu et ce qui a réellement été construit, et pourquoi ?

---

### 9. `project-docs/PROJECT_WORKFLOW.md` — comment le travail circule-t-il réellement, et quel document dois-je toucher et quand ?

| Section | Traitement |
|---|---|
| Quel document mettre à jour, et quand | Générique — le tableau qui fait le tissu conjonctif |
| Suivi du travail | Motif générique, conditionné par l'outil réellement employé |
| Format de user story | Générique — renvoi vers le gabarit partagé, voir le §8 ci-dessus |
| Définition du terminé | Générique |
| Référence de vocabulaire | Générique |
| Étapes d'amorçage de l'outil de suivi | Motif générique |

**Quel document mettre à jour, et quand**
1. Pour chaque document, quel événement du monde réel devrait déclencher sa mise à jour ?
2. Un document est-il mis à jour selon un calendrier au lieu de l'être quand le fait qu'il porte change réellement — signe qu'il n'est pas le bon propriétaire de ce fait ?

**Suivi du travail**
1. Quel outil suivra réellement le travail — un tableau, un tableur, de simples issues ?
2. Par quels états le travail passe-t-il, et qui l'y fait passer ?
3. Des champs personnalisés sont-ils réellement nécessaires, ou la ligne `Statut` du format de user story suffit-elle déjà ?

**Définition du terminé (au niveau du projet)**
1. Quel est le seuil universel que chaque user story doit franchir avant d'être terminée, indépendamment de sa propre liste de contrôle ?

**Référence de vocabulaire**
1. Chaque terme employé à travers les spécifications est-il traçable jusqu'à une entrée du glossaire ?

**Étapes d'amorçage de l'outil de suivi**
1. Quelles sont les étapes de réglage, à faire une seule fois, dont a besoin quelqu'un qui démarre de zéro, dans l'ordre, avant que la première user story puisse être créée ?

---

### 10. `CLAUDE.md` — de quoi chaque session a-t-elle besoin avant de toucher à quoi que ce soit ?

Toutes génériques — c'est ce que la section « `CLAUDE.md` se construit en dernier » de `01` enseigne déjà ; ces questions sont la façon de le remplir concrètement.

**Ce qu'est ce projet**
1. En 2-3 phrases, qu'est-ce que c'est et pour qui est-ce ?
2. Quel est le seul fait d'architecture qu'une session fraîche doit absolument connaître avant de toucher un fichier ?

**Carte des dossiers**
1. Quels sont les dossiers de premier niveau, et quelle est la raison en une ligne de l'existence de chacun ?
2. Y a-t-il une convention de nommage qui a besoin d'être énoncée explicitement pour ne jamais être devinée ?

**Pile technique**
1. Quelle est la pile pour chaque partie majeure du système ?
2. Où le détail canonique est-il déjà documenté, pour que cette section reste un renvoi au lieu d'une reformulation ?

**Conventions**
1. Quelle est une erreur qui s'est déjà produite une fois, et que cette section existe précisément pour empêcher ?
2. Quelle règle de nommage ou de mise en forme un nouveau contributeur se tromperait sans qu'on le lui dise directement ? Pour chaque langage et chaque couche réellement employés : quelle est la règle de casse pour les fichiers, les classes et les composants, les variables et les fonctions, les booléens et les constantes — énoncée explicitement, et non laissée à déduire du premier fichier qui a par hasard fait précédent ? (Voir la section « Conventions de nommage » de l'`AGENTS.md` de ce kit pour la forme que cela devrait prendre.)
3. Y a-t-il une convention de nommage des dossiers de service ou de module (dès que le projet a plus d'une pièce exécutée indépendamment), et est-elle énoncée ici plutôt que laissée implicite ?

**Contraintes de confidentialité**
1. Qu'est-ce qui ne doit jamais être révélé, dit ou inventé, et que devrait-il se passer à la place quand quelqu'un le demande quand même ?
2. Y a-t-il quelque chose d'autorisé à l'usage qui était auparavant restreint — le tableau est-il réellement à jour ?

**Liste de contrôle de la première session**
1. Quel est le chemin le plus rapide pour être utile, pour quelqu'un qui connaît déjà ce projet, par opposition à quelqu'un qui démarre de zéro ?
2. Dans quel ordre les documents de base devraient-ils être lus ?

**Renvois**
1. Pour la poignée de choses qui reviennent sans arrêt en cours de session, quel document unique est canonique pour chacune ?

## Tableau des erreurs courantes

| Erreur | Pourquoi cela arrive | Le correctif |
|---|---|---|
| Copier les intitulés de section exacts d'un document dans un nouveau projet au lieu du motif sous-jacent | L'intitulé existe déjà, il paraît sans risque de le réemployer mot pour mot | Demandez « générique, à généraliser, ou conditionnelle ? » pour chaque intitulé avant de le réemployer — voir l'entrée du PRD ci-dessus pour ce à quoi cela ressemble bien fait |
| Imposer une liste de sections figée à un type de document censé être incrémental (les spécifications fonctionnelles et techniques) | La cohérence donne l'impression de devoir s'appliquer partout | Certains documents sont délibérément façonnés par ce qui est déjà réel, et non par un gabarit — écrire des sections avant qu'une user story se close est de la spéculation, pas de la documentation |
| Répondre à ces questions de réflexion de façon générique au lieu de le faire avec les spécificités réelles du projet | Il est plus rapide d'écrire quelque chose qui sonne plausible que d'y réfléchir | Les questions sont l'échafaudage, pas le contenu — une réponse qui conviendrait à n'importe quel projet n'a pas réellement répondu à la question |
| Traiter une section conditionnelle comme obligatoire parce qu'elle figure dans la liste | La liste a l'air complète, donc en sauter un élément donne l'impression d'une omission | « À sauter si non applicable » est en soi la bonne réponse pour une section conditionnelle sur un projet où elle ne s'applique pas — n'y forcez pas de contenu |
