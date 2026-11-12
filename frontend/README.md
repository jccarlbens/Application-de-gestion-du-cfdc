---
created: 2026-11-12T00:00:00Z
updated: 2026-11-12T15:52:22Z
---

# frontend — interface de l'application CFDC

React + TypeScript + Vite, organisé en **Feature-Sliced Design** (`project-docs/_ARCHITECTURE_EXPLAINED.md`, partie 3). Interface en français, bleu et blanc.

## Commandes

Depuis `frontend/`, avec Node 22 :

| Pour… | Commande |
|---|---|
| Installer | `npm ci` |
| Développer (port 5173) | `npm run dev` — relaie `/api` vers `http://localhost:8000`, ou vers `BACKEND_URL` |
| Tester | `npm test` |
| Vérifier le code | `npm run lint` |
| Vérifier l'architecture | `npm run lint:arch` (Steiger) |
| Construire | `npm run build` |

## Organisation

- `src/app/` : providers, routeur, styles. `src/pages/`, puis `widgets/`, `features/`, `entities/` au fil des user stories ; `src/shared/` : client HTTP, configuration.
- `tests/pure/` : sans DOM ni React (vérifié par `tests/pure/no-dom.test.ts`) ; `tests/rendered/` : avec Testing Library.
- Un type renvoyé par le serveur (`…Dto`) reste dans un segment `api` et se transforme en type de l'application avant d'en sortir.

## En conteneur

`Dockerfile` construit l'interface et la sert avec **Nginx**, qui relaie `/api` vers le backend (`nginx/default.conf.template`). Variables : `PORT` (8080 par défaut) et `BACKEND_URL` (`http://backend:8000` dans Docker Compose).
