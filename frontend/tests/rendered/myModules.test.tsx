import { screen, within } from '@testing-library/react'
import { MyModulesPage } from '../../src/pages/my-modules'
import { json, me, renderApp } from './renderApp'

const MINE = [
  {
    id: 't-2', title: 'Accueil VIP', description: null, domain_name: 'Accueil', subdomain_name: 'Protocole',
    modules: [{ id: 'm-3', title: 'Salutations', description: null, documents: [] }],
  },
  {
    id: 't-1', title: 'Rampe', description: 'Pour la piste', domain_name: 'Sûreté-Sécurité', subdomain_name: 'Conduite sur la rampe',
    modules: [
      {
        id: 'm-1', title: 'Vitesses', description: 'Les limites',
        documents: [{ id: 'd-1', file_name: 'Vitesses.pdf', size_bytes: 2.4 * 1024 * 1024, uploaded_at: '2026-11-20T10:00:00Z' }],
      },
      { id: 'm-2', title: 'Balisage', description: null, documents: [] },
    ],
  },
]

afterEach(() => {
  vi.unstubAllGlobals()
})

describe('MyModulesPage', () => {
  it('montre les formations du formateur, leurs modules et leurs documents', async () => {
    renderApp(<MyModulesPage />, {
      at: '/mes-modules', path: '/mes-modules',
      responses: { '/auth/me': () => json(me(['trainer'])), '/me/modules': () => json(MINE) },
    })
    const titles = await screen.findAllByRole('heading', { level: 2 })
    expect(titles.map((h) => h.textContent)).toEqual(['Accueil VIP', 'Rampe'])
    expect(screen.getByText('Sûreté-Sécurité › Conduite sur la rampe')).toBeInTheDocument()
    expect(screen.getByText('Pour la piste')).toBeInTheDocument()
    const docs = screen.getByRole('list', { name: 'Documents de « Vitesses »' })
    expect(within(docs).getByRole('link', { name: 'Vitesses.pdf' })).toHaveAttribute('href', '/api/v1/documents/d-1/download')
    expect(within(docs).getByText('2,4 Mo · 20/11/2026')).toBeInTheDocument()
    expect(screen.getAllByText('Pas encore de document pour ce module.')).toHaveLength(2)
    expect(screen.queryByText(/Admin/)).not.toBeInTheDocument()
  })

  it("dit qu'aucun module n'est confié", async () => {
    renderApp(<MyModulesPage />, {
      at: '/mes-modules', path: '/mes-modules',
      responses: { '/auth/me': () => json(me(['trainer'])), '/me/modules': () => json([]) },
    })
    expect(await screen.findByText("Aucun module ne vous est confié pour l'instant.")).toBeInTheDocument()
  })

  it('est ouverte à une personne formateur et direction', async () => {
    renderApp(<MyModulesPage />, {
      at: '/mes-modules', path: '/mes-modules',
      responses: { '/auth/me': () => json(me(['direction', 'trainer'])), '/me/modules': () => json(MINE) },
    })
    expect(await screen.findByRole('heading', { name: 'Rampe' })).toBeInTheDocument()
  })

  it("n'est pas ouverte aux autres rôles", async () => {
    renderApp(<MyModulesPage />, { at: '/mes-modules', path: '/mes-modules', responses: { '/auth/me': () => json(me(['secretary'])) } })
    expect(await screen.findByText("Vous n'avez pas accès à cette page.")).toBeInTheDocument()
  })
})
