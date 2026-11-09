---
created: 2026-11-09T00:00:00Z
updated: 2026-11-09T17:14:13Z
---

@AGENTS.md

## Claude Code

*(Instructions propres à Claude Code uniquement. Ne dupliquez pas le contenu d'`AGENTS.md` ici.)*

### Les compétences `epic` et `user-story` : suivi sur GitHub

**Décision à prendre** (`project-docs/PROJECT_WORKFLOW.md` § Suivi du travail). Le dépôt est déjà renseigné dans les deux compétences : `jccarlbens/Application-de-gestion-du-cfdc`. Si un tableau GitHub Projects est utilisé, remplacez `[TRACKER_PROJECT_NUMBER]` et `[Tracker Project Name]` dans `.claude/skills/user-story/SKILL.md` ; sinon, adaptez les étapes `gh` à l'outil retenu.

**Avant de créer une user story, vérifiez que le Milestone de son Epic existe.** S'il manque, arrêtez-vous et demandez.

### Toujours demander

**L'utilisateur veut qu'on lui demande toujours des précisions.** Dès qu'un point est ambigu ou non décidé, posez la question au lieu de supposer, et ne rédigez une section qu'après sa réponse.

### Langue

**Répondez en français.** La prose est en français ; les chemins, les noms de fichiers et tous les identifiants de code sont en anglais.
