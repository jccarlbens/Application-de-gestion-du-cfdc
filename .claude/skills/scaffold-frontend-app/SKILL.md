---
name: scaffold-frontend-app
description: Générer la structure d'un nouveau frontend React + TypeScript + Vite en Feature-Sliced Design, avec Tailwind, React Router, TanStack Query, Zustand, Steiger et Vitest câblés. À utiliser une fois que les documents du projet existent et qu'il est temps de poser la véritable arborescence du frontend. Le pendant de scaffold-backend-service. Scaffold a React + TypeScript + Vite frontend on Feature-Sliced Design.
created: 2026-09-16T20:15:00Z
updated: 2026-11-09T17:14:13Z
---

# Compétence : générer la structure d'une application frontend

## Pourquoi elle existe

Lisez d'abord la **partie 3** de `project-docs/_ARCHITECTURE_EXPLAINED.md` si le *pourquoi* d'une pièce quelconque ici n'est pas clair — les couches, la règle d'import, la convention d'API publique et l'emplacement de chaque bibliothèque y sont tous expliqués. Cette compétence couvre le *comment*.

Elle existe pour qu'un frontend démarre à la forme établie plutôt qu'à *« un seul dossier `components/`, on rangera plus tard »* — qui est la forme à laquelle démarre chaque frontend et qu'aucun ne range plus tard.

## Précondition dure — ne pas sauter

**Aucun fichier source n'est créé avant que le périmètre ne soit convenu.** Avant d'exécuter cette compétence :

- `project-docs/PRD.md`, `NFR.md`, `SOLUTION_DESIGN.md` et `PLAN.md` doivent déjà exister et être remplis.
- `SOLUTION_DESIGN.md` §5 doit consigner que cette pile technique a été **choisie**, et non adoptée par défaut. `_ARCHITECTURE_EXPLAINED.md` est une proposition ; un projet qui ne l'a pas acceptée ne doit pas être généré à partir d'elle.

S'il manque l'un ou l'autre, **arrêtez-vous et dites-le.** Ne générez rien, et dites que le périmètre doit d'abord être convenu.

**Un contrôle de plus, propre à cette compétence :** confirmez que le projet a réellement besoin d'une application frontend séparée. Un backend qui rend ses propres gabarits n'en a pas besoin, et un projet de trois pages statiques non plus. Six couches imposées à un site vitrine, c'est pire qu'aucune structure.

## Ce que cette compétence ne fait *pas*

Elle ne construit que l'**infrastructure** : l'application Vite, les dossiers de couches, les providers, le routeur, le linting et le montage des tests.

Elle ne crée **aucune entity, aucune feature et aucun widget.** Ce sont du vrai travail, ajouté par user story, exactement comme la génération backend ne crée aucun `dal_*.py`. Un frontend fraîchement généré affiche une page presque vide.

**Elle ne crée pas non plus `entities/`, `features/` ni `widgets/` sous forme de dossiers vides.** C'est délibéré et c'est la partie peu évidente : Steiger produit des constats sur les slices vides, insignifiantes ou contournées, donc précréer trois couches vides revient à remettre à un étudiant un linter rouge sur un projet où il n'a rien écrit. **Une couche est créée par la première user story qui en a besoin.** La recommandation de FSD elle-même est que vous n'êtes pas obligé d'utiliser toutes les couches — seulement que leurs noms sont fixés quand vous les utilisez.

## Procédure

```
Avancement de la génération :
- [ ] Étape 1 : confirmer la précondition
- [ ] Étape 2 : créer l'application Vite
- [ ] Étape 3 : installer la pile technique
- [ ] Étape 4 : câbler Tailwind
- [ ] Étape 5 : créer le squelette FSD
- [ ] Étape 6 : câbler les providers et le routeur
- [ ] Étape 7 : installer Steiger, et prouver qu'il mord
- [ ] Étape 8 : câbler Vitest, et prouver qu'il s'exécute
- [ ] Étape 9 : vérifier que ça démarre
- [ ] Étape 10 : rapporter
```

---

**Étape 1 — Confirmer la précondition.** Voir ci-dessus. Arrêtez-vous ici s'il manque quoi que ce soit.

**Étape 2 — Créer l'application Vite.**

```bash
npm create vite@latest <dossier-app> -- --template react-ts
cd <dossier-app>
npm install
```

`<dossier-app>` est généralement `frontend/`. Quel qu'il soit, il est **à plat à la racine du dépôt**, à côté du backend — et non imbriqué dedans.

**Étape 3 — Installer la pile technique.**

```bash
npm i react-router-dom @tanstack/react-query zustand
npm i -D tailwindcss @tailwindcss/vite
npm i -D vitest jsdom @testing-library/react @testing-library/jest-dom @testing-library/user-event
npm i -D steiger @feature-sliced/steiger-plugin
```

**N'ajoutez pas une bibliothèque que les documents n'ont pas demandée.** Si `SOLUTION_DESIGN.md` ne dit rien de l'état client global, installez Zustand quand même — il fait partie de la pile acceptée — mais n'ajoutez pas de votre propre initiative une bibliothèque de formulaires, de dates, de composants ou un jeu d'icônes. Ce sont des décisions prises par user story.

**Étape 4 — Câbler Tailwind.** Deux modifications, et l'import CSS est celle que les gens oublient.

`vite.config.ts` :

```ts
/// <reference types="vitest/config" />
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'

export default defineConfig({
  plugins: [react(), tailwindcss()],
  test: {
    environment: 'jsdom',
    globals: true,
    setupFiles: './src/shared/config/test-setup.ts',
  },
})
```

`src/app/styles/index.css` — remplacez tout le fichier que Vite a généré :

```css
@import "tailwindcss";
```

**`vitest/config`, et non `vitest`, dans cette première ligne.** Le `/// <reference types="vitest" />` nu est ce que montrent tous les guides plus anciens, et sous Vite 8 avec Vitest 5 il ne type pas du tout la clé `test` : `tsc` signale `TS2769: Object literal may only specify known properties, and 'test' does not exist in type 'UserConfigExport'`, sur ce fichier-ci, ce qui rend inatteignable la compilation propre de l'étape 9. Un segment de chemin est tout le correctif. (La page de configuration de Vitest elle-même le porte.)

**Tailwind 4 n'a ni `tailwind.config.js` ni étape PostCSS.** Si vous vous retrouvez à lancer `npx tailwindcss init`, vous suivez un guide pour la version 3. Supprimez les `src/App.css` et `src/index.css` générés.

**Étape 5 — Créer le squelette FSD.** Seulement les couches qu'une génération de structure peut honnêtement remplir :

```
src/
  app/
    index.tsx            <- les providers, composés
    router.tsx           <- la table de routes
    styles/index.css     <- l'import Tailwind
  pages/
    home/
      index.ts           <- API publique : export { HomePage } from './ui/HomePage'
      ui/HomePage.tsx
  shared/
    api/index.ts         <- le client HTTP, et rien d'autre pour l'instant
    config/index.ts      <- la lecture de l'environnement
    config/test-setup.ts
    lib/index.ts
    ui/index.ts
  main.tsx
```

Puis **supprimez** `src/App.tsx`, `src/App.css`, `src/index.css` et `src/assets/`.

**`src/main.tsx` est le seul fichier qui reste à la racine de `src/`, et ce n'est pas une exception à discuter.** C'est le module vers lequel le bundler est pointé depuis `index.html` ; il n'appartient à aucune couche parce qu'il est ce qui passe le contrôle *aux* couches, et il ne fait rien d'autre que monter `<App />`. Chaque *autre* fichier à la racine de `src/` n'appartient lui non plus à aucune couche, et c'est un défaut — le premier qui survit apprend à tout le monde que la règle est facultative.

**Ce que laisse le gabarit change d'une version à l'autre, donc lisez le dossier plutôt que cette liste.** `create-vite@9` livre un `src/assets/hero.png` à côté de `react.svg`, et il livre **oxlint** plutôt qu'ESLint : un `.oxlintrc.json` à la racine et un script `"lint": "oxlint"`. Gardez les deux. Oxlint est un linter de *code* et Steiger un linter d'*architecture* — ils ne se recouvrent pas, `lint` et `lint:arch` sont deux scripts exprès, et un projet veut les deux.

**`shared/api/index.ts` est là où vit la frontière réseau.** Un client mince, et des modules par ressource ajoutés par les user stories qui en ont besoin. La règle de la partie 3 qui compte le plus ici : **un type de DTO serveur est déclaré dans un segment `api` et transformé vers votre propre type avant de le quitter.** Nommez-les distinctement — `UserDto` et `User` — et n'exportez jamais le `Dto`.

**Étape 6 — Câbler les providers et le routeur.**

`src/app/index.tsx` :

```tsx
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { RouterProvider } from 'react-router-dom'
import { router } from './router'
import './styles/index.css'

const queryClient = new QueryClient()

export function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <RouterProvider router={router} />
    </QueryClientProvider>
  )
}
```

`src/app/router.tsx` porte la table de routes et importe depuis `pages/` — **la seule couche qui en a le droit.**

`src/main.tsx` monte `<App />` et ne fait rien d'autre.

**Étape 7 — Installer Steiger, et prouver qu'il mord.** C'est l'étape qui rend l'architecture réelle, et sauter la preuve est la façon dont un projet finit avec un linter qui n'a jamais rien vérifié.

`steiger.config.js` à la racine de l'application :

```js
import { defineConfig } from 'steiger'
import fsd from '@feature-sliced/steiger-plugin'

export default defineConfig([
  ...fsd.configs.recommended,
])
```

Ajoutez aux scripts de `package.json` : `"lint:arch": "steiger ./src"`.

Lancez `npx steiger ./src` — cela doit passer.

**Maintenant prouvez que ça échoue.** Ajoutez un import vers le haut délibéré dans une couche basse — dans `src/shared/lib/index.ts`, écrivez `import { HomePage } from '../../pages/home'`. Relancez. **Cela doit signaler `fsd/forbidden-imports`.** Si cela passe, le linter n'est pas branché sur votre code source et chaque garantie de la partie 3 est décorative. Retirez la ligne et confirmez que cela redevient vert.

Ne passez pas à la suite avant d'avoir vu passer au rouge puis au vert.

**Étape 8 — Câbler Vitest, et prouver qu'il s'exécute.**

`src/shared/config/test-setup.ts` :

```ts
import '@testing-library/jest-dom/vitest'
```

Ajoutez aux scripts de `package.json` : `"test": "vitest run"`.

**Découpez les tests comme le code source est découpé**, dans `tests/` à côté de `src/` :

- `tests/pure/` — pas de DOM, pas de React. C'est là que `shared/lib` et toute logique de transformation est testée, et ces tests s'exécutent en millisecondes.
- `tests/rendered/` — tout ce qui rend quelque chose, avec Testing Library.

Écrivez **un** test trivial dans chacun, pour que le découpage existe dès le premier commit au lieu d'être rétro-ajouté, et lancez `npm test` pour les voir passer. Un dossier de tests créé vide est un dossier de tests dans lequel personne ne met le premier test.

#### Mettez `tests/` à l'intérieur de TypeScript, parce que `create-vite` ne le fait pas

**C'est l'étape sans message d'erreur, et c'est donc celle qu'on saute.** `tsconfig.app.json` est livré avec `"include": ["src"]`, et `tsconfig.json` ne référence que les projets `app` et `node`. `tests/` n'est donc dans aucun projet TypeScript : `npm test` exécute les fichiers, `tsc -b` ne les ouvre jamais, et **`npm run build` annonce une compilation propre sur des fichiers de test que le vérificateur de types n'a pas lus.** Mettez `const broken: number = 'not a number'` dans un test et regardez la compilation passer — puis corrigez.

`tsconfig.test.json`, à côté des autres :

```jsonc
{
  "extends": "./tsconfig.app.json",
  "compilerOptions": {
    "tsBuildInfoFile": "./node_modules/.tmp/tsconfig.test.tsbuildinfo",
    // `node` n'est pas facultatif, et l'omettre vous égare sérieusement : tout
    // test qui lit le système de fichiers reçoit `any` de `readdirSync`, et
    // l'erreur qui apparaît parle de l'arité des tuples de `it.each`, à
    // plusieurs cadres du paquet de types manquant qui l'a causée.
    //
    // `vitest/globals` est ce dont `globals: true` a besoin. Cela met
    // describe/it/expect dans la portée à l'exécution ; rien ne les met dans
    // la portée du vérificateur de types.
    "types": ["node", "vite/client", "vitest/globals", "@testing-library/jest-dom/vitest"]
  },
  "include": ["tests"]
}
```

Puis ajoutez `{ "path": "./tsconfig.test.json" }` aux `references` de `tsconfig.json`.

Relancez `npx tsc -b --force` avec l'erreur de type délibérée encore en place. **Cela doit maintenant échouer.** Retirez-la et confirmez que cela passe. Même discipline qu'à l'étape 7 : regardez le contrôle mordre avant de le croire.

#### La règle sur `tests/pure` reçoit un test, pas une convention

Un test dans `tests/pure/` qui importe React est un bogue dans le test, et une règle que personne ne vérifie est décorative — ce qui est tout l'argument de l'étape 7, appliqué un dossier plus loin. `tests/pure/no-dom.test.ts` :

```ts
import { readdirSync, readFileSync } from 'node:fs'
import { fileURLToPath } from 'node:url'
import { dirname, join } from 'node:path'

// `pure/` et `rendered/` se séparent sur un seul fait : est-ce que le test
// rend quelque chose ? C'est vérifiable, donc c'est vérifié - sinon les
// dossiers deviennent une habitude de classement que personne n'applique, et
// un test mal classé rend le découpage insignifiant, en silence.
//
// Deux détails sont porteurs. Le répertoire vient de `import.meta.url`, et non
// de `process.cwd()`, pour que le test ne dépende pas de l'endroit d'où vitest
// a été lancé. Et ce fichier s'exclut lui-même : ses propres assertions
// contiennent précisément les chaînes qu'il interdit, donc un fichier qui se
// surveille lui-même échoue toujours.
const HERE = dirname(fileURLToPath(import.meta.url))
const FILES = readdirSync(HERE).filter(
  (f) => /\.test\.tsx?$/.test(f) && f !== 'no-dom.test.ts',
)

describe('les tests de pure/ ne touchent aucun DOM', () => {
  it('trouve les fichiers qu\'il doit surveiller', () => {
    expect(FILES.length).toBeGreaterThan(0)
  })

  it.each(FILES)('%s n\'importe aucune bibliothèque de rendu', (file) => {
    const source = readFileSync(join(HERE, file), 'utf-8')
    expect(source).not.toContain('@testing-library')
    expect(source).not.toContain('from "react"')
    expect(source).not.toContain("from 'react'")
  })
})
```

Prouvez celui-ci aussi : ajoutez un import de React dans l'autre test de `pure/`, regardez-le échouer, retirez-le.

**Étape 9 — Vérifier que ça démarre.** Ne supposez pas que la structure générée est correcte — prouvez-le :

1. `npm run dev`, en arrière-plan ou dans un autre terminal.
2. Ouvrez l'URL servie. La page d'accueil s'affiche, avec le style Tailwind **visiblement appliqué** — **vérifiez qu'une vraie classe Tailwind a un effet**, parce qu'un `@import "tailwindcss"` manquant échoue en silence et ressemble à du HTML sans style plutôt qu'à une erreur.
3. La console du navigateur est propre — pas d'erreur de provider, pas d'avertissement de routeur.
4. `npm run build` s'achève sans aucune erreur TypeScript.
5. Arrêtez le serveur.

**Étape 10 — Rapporter.** Confirmez chaque fichier créé, que ça démarre, que `npm run build` est propre, **que Steiger a été vu échouer sur une violation délibérée puis repasser**, et que `npm test` exécute les deux dossiers de tests.

Dites ensuite ce qui vient après : la première vraie user story, via la création de `user-story` — c'est elle qui ajoutera la première slice d'`entities/`, de `features/` ou de `widgets/`, et avec elle la première couche que cette génération de structure n'a délibérément pas créée.

## Ce qui a réellement été exécuté, et quand

**Exécutée de bout en bout dans un répertoire jetable le 2026-10-02**, chaque étape y compris le rouge-puis-vert de l'étape 7 et la compilation de l'étape 9. Avant cette date, **aucune partie de cette compétence n'avait jamais été exécutée** — elle avait été écrite à partir de documentation consultée, ce qui est bien sourcé et n'est pas la même chose.

Versions auxquelles elle a été observée fonctionnelle : `create-vite@9.2.1`, Vite 8.3, React 19.2, TypeScript 6.0, Vitest 5.0, Tailwind 4.3, `steiger@0.6` avec `@feature-sliced/steiger-plugin@0.8`, React Router 7.18, TanStack Query 5.104, Zustand 5.0, Node 22.16.

Ce que cette exécution a changé : la référence `vitest/config` de l'étape 4, la liste de suppressions de l'étape 5 et sa note sur `main.tsx`, et les deux nouvelles sous-sections de l'étape 8. Les étapes 2, 3, 6, 7 et 9 n'ont eu besoin d'aucune correction — **l'affirmation de l'étape 7 selon laquelle Steiger signale `fsd/forbidden-imports` sur un import `shared → pages` a été vue être exactement vraie**, et `fsd/insignificant-slice` ne se déclenche *pas* sur une structure fraîchement générée, parce que l'étape 5 ne crée aucun `widgets/`, `features/` ni `entities/` sur quoi il pourrait se déclencher.

**Traitez la liste de versions comme la chose la plus susceptible d'être obsolète.** Quatre des cinq défauts trouvés par cette exécution venaient d'un outil qui avait bougé, et non d'une étape qui était fausse.

## Les deux erreurs que cette compétence existe pour empêcher

**Mettre un fichier à la racine de `src/`.** Il y a toujours une raison pour le premier. Chaque fichier d'après cite le premier comme précédent, et en un mois les couches ne décrivent plus que la moitié de la base de code.

**Laisser voyager un DTO serveur.** `fetch` renvoie la forme du serveur ; le geste tentant est de la passer directement à un composant. Dès que trois composants lisent `user.first_name` parce que c'est ainsi que l'API l'appelle, votre format réseau est votre contrat d'interface et le backend ne peut plus renommer un champ. Transformez à la frontière, dans un segment `api`, chaque fois — **surtout quand les deux formes sont identiques aujourd'hui**, parce que c'est à ce moment-là que cela paraît le plus inutile et que le couplage est le moins coûteux à empêcher.
