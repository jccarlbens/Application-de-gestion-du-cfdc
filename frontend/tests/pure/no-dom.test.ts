import { readdirSync, readFileSync } from 'node:fs'
import { fileURLToPath } from 'node:url'
import { dirname, join } from 'node:path'

// `pure/` et `rendered/` se séparent sur un seul fait : est-ce que le test
// rend quelque chose ? C'est vérifiable, donc c'est vérifié. Ce fichier
// s'exclut lui-même : ses assertions contiennent les chaînes qu'il interdit.
const HERE = dirname(fileURLToPath(import.meta.url))
const FILES = readdirSync(HERE).filter(
  (f) => /\.test\.tsx?$/.test(f) && f !== 'no-dom.test.ts',
)

describe('les tests de pure/ ne touchent aucun DOM', () => {
  it("trouve les fichiers qu'il doit surveiller", () => {
    expect(FILES.length).toBeGreaterThan(0)
  })

  it.each(FILES)("%s n'importe aucune bibliothèque de rendu", (file) => {
    const source = readFileSync(join(HERE, file), 'utf-8')
    expect(source).not.toContain('@testing-library')
    expect(source).not.toContain('from "react"')
    expect(source).not.toContain("from 'react'")
  })
})
