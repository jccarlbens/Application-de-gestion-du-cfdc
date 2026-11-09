---
created: 2026-09-08T17:38:40Z
updated: 2026-11-09T17:14:13Z
---

# Prompt de démarrage — à copier tel quel dans votre agent

**À utiliser pour remplir les documents de `project-docs/`.** Ce prompt fonctionne avec n'importe quel agent (Claude Code, ou tout autre outil de codage agentique) — il ne dépend d'aucun mécanisme propre à un outil.

```text
Ce projet contient une structure de documentation à remplir. Tous les
documents sont sous project-docs/, et ils se remplissent dans cet ordre :

  project-docs/PRD.md
  project-docs/NFR.md
  project-docs/SOLUTION_DESIGN.md
  project-docs/PLAN.md
  project-docs/GLOSSARY.md          (à finaliser en dernier, quand on saura ce qu'est ce produit)
  project-docs/PROJECT_WORKFLOW.md  (tout en dernier)

Chaque section contient des questions de réflexion (citées avec « > »).
Guide-moi à travers ces documents, dans cet ordre, une section à la fois :
pose-moi les questions de cette section, attends ma réponse, n'invente rien
à ma place. Une fois que j'ai répondu, écris la section à partir de ma
réponse et montre-la-moi avant de passer à la suivante.

Réponds-moi en français.

Ne touche pas encore à AGENTS.md ni à CLAUDE.md, et ne crée rien sous
project-docs/execution/, functional-specs/, technical-specs/, reviews/ ni
learnings/. Cela vient plus tard : AGENTS.md et CLAUDE.md sont des résumés
de tout ce qui précède et s'écrivent en dernier, et le reste ne se remplit
que lorsqu'il y a du travail réel à consigner.
```

**Avant de le coller**, lisez une fois `project-docs/_ARCHITECTURE_EXPLAINED.md`. C'est le seul document du kit qui répond au lieu de questionner, et `SOLUTION_DESIGN.md` ira plus vite si vous savez déjà lesquelles de ses recommandations vous retenez.

**Une fois les six documents remplis**, écrivez `AGENTS.md` et `CLAUDE.md` à partir d'eux, puis planifiez votre premier Epic (compétence `epic`) et sa première user story (compétence `user-story`) — et seulement ensuite générez la structure du code (`scaffold-backend-service`, puis `scaffold-frontend-app`).

**Ce qui doit se produire** : l'agent doit vous poser une question à la fois, attendre votre réponse, puis rédiger — et non vous rendre les six documents remplis d'un coup. Si l'agent se met à tout rédiger sans rien vous demander, arrêtez-le et recollez le prompt : c'est exactement le comportement que ce prompt sert à empêcher.

> **Une note sur la langue.** Ce kit est la version française, et sa prose est en français. **Les chemins, les noms de fichiers et tous les identifiants de code restent en anglais** — `project-docs/`, `PRD.md`, `SOLUTION_DESIGN.md`, les couches `entities / dal / bll / api`, les préfixes `ent_`, `dal_`, `bll_`, et les couches Feature-Sliced Design `app / pages / widgets / features / entities / shared`. Ce n'est pas un oubli de traduction : les noms de couches FSD sont fixés par la méthode et le linter Steiger les reconnaît littéralement, les préfixes du backend sont vérifiés par un test, et c'est le vocabulaire que vous lirez dans toute la documentation technique du reste de votre carrière.
