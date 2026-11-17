import { screen } from '@testing-library/react'
import { SectionPage } from '../../src/pages/section'
import { json, me, renderApp } from './renderApp'

afterEach(() => {
  vi.unstubAllGlobals()
})

describe('SectionPage', () => {
  it('montre « Bientôt disponible » pour un menu de la personne', async () => {
    renderApp(<SectionPage menuKey="comptes" />, {
      at: '/comptes',
      path: '/comptes',
      responses: { '/auth/me': () => json(me(['coordinator'])) },
    })
    expect(await screen.findByRole('heading', { level: 1 })).toHaveTextContent('Comptes')
    expect(screen.getByText('Bientôt disponible.')).toBeInTheDocument()
  })

  it("refuse un menu que la personne n'a pas, même en tapant l'adresse", async () => {
    renderApp(<SectionPage menuKey="comptes" />, {
      at: '/comptes',
      path: '/comptes',
      responses: { '/auth/me': () => json(me(['trainer'])) },
    })
    expect(await screen.findByText("Vous n'avez pas accès à cette page.")).toBeInTheDocument()
    expect(screen.queryByText('Bientôt disponible.')).not.toBeInTheDocument()
  })
})
