import { screen, within } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { HomePage } from '../../src/pages/home'
import { json, me, renderApp } from './renderApp'

const HEALTH = () => json({ status: 'ok', database: 'reachable' })

afterEach(() => {
  vi.unstubAllGlobals()
})

describe('HomePage', () => {
  it('affiche la personne, ses rôles en français et ses raccourcis', async () => {
    renderApp(<HomePage />, { responses: { '/auth/me': () => json(me(['secretary', 'trainer'])), '/health': HEALTH } })

    expect(await screen.findByRole('heading', { level: 1 })).toHaveTextContent('Connecté : Marie Joseph (B07-42)')
    expect(screen.getByText('Rôles : Secrétaire, Formateur')).toBeInTheDocument()
    const shortcuts = screen.getByRole('heading', { name: 'Accès rapide' }).nextElementSibling as HTMLElement
    expect(within(shortcuts).getAllByRole('link').map((l) => l.textContent)).toEqual([
      'Formations',
      'Mes modules',
      'Demandes de formation',
      'Sessions et calendrier',
      'Participants',
    ])
    expect(await screen.findByText('Le serveur et la base de données répondent.')).toBeInTheDocument()
  })

  it("le menu d'un formateur ne montre que « Mes modules »", async () => {
    renderApp(<HomePage />, { responses: { '/auth/me': () => json(me(['trainer'])), '/health': HEALTH } })
    const nav = await screen.findByRole('navigation', { name: 'Menu principal' })
    expect(within(nav).getAllByRole('link').map((l) => l.textContent)).toEqual(['Accueil', 'Mes modules'])
  })

  it("renvoie vers la connexion quand personne n'est connecté", async () => {
    renderApp(<HomePage />, { responses: { '/auth/me': () => json({ detail: "Vous n'êtes pas connecté." }, 401) } })
    expect(await screen.findByText('Page de connexion')).toBeInTheDocument()
  })

  it('signale une session expirée en revenant à la connexion', async () => {
    renderApp(<HomePage />, {
      responses: { '/auth/me': () => json({ detail: 'Votre session a expiré, reconnectez-vous.' }, 401) },
    })
    expect(await screen.findByText('Page de connexion?expiree=1')).toBeInTheDocument()
  })

  it('se déconnecte et revient à la connexion', async () => {
    const fetchMock = renderApp(<HomePage />, {
      responses: {
        '/auth/me': () => json(me(['it_admin'])),
        '/health': HEALTH,
        '/auth/logout': () => new Response(null, { status: 204 }),
      },
    })
    await userEvent.setup().click(await screen.findByRole('button', { name: 'Se déconnecter' }))
    expect(await screen.findByText('Page de connexion')).toBeInTheDocument()
    expect(fetchMock.mock.calls.some(([url]) => String(url).endsWith('/auth/logout'))).toBe(true)
  })

  it('le bouton « Menu » ouvre et ferme le menu (téléphone)', async () => {
    renderApp(<HomePage />, { responses: { '/auth/me': () => json(me(['secretary'])), '/health': HEALTH } })
    const button = await screen.findByRole('button', { name: 'Menu' })
    const nav = screen.getByRole('navigation', { name: 'Menu principal' })
    expect(button).toHaveAttribute('aria-expanded', 'false')
    expect(nav.className).toContain('hidden')

    await userEvent.setup().click(button)
    expect(button).toHaveAttribute('aria-expanded', 'true')
    expect(nav.className).not.toMatch(/(^|\s)hidden(\s|$)/)
  })
})
