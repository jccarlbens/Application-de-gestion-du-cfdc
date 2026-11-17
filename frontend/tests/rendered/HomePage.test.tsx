import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { MemoryRouter, Route, Routes, useLocation } from 'react-router-dom'
import { HomePage } from '../../src/pages/home'

const ME = { badge: 'B07-42', first_name: 'Marie', last_name: 'Joseph', roles: ['secretary'] }

function json(body: unknown, status = 200): Response {
  return new Response(JSON.stringify(body), { status })
}

function LoginSpy() {
  const location = useLocation()
  return <p>Page de connexion{location.search}</p>
}

function renderHome(responses: Record<string, () => Response | Promise<Response>>) {
  const fetchMock = vi.fn((url: string) => {
    const path = Object.keys(responses).find((p) => url.endsWith(p))
    return path ? Promise.resolve(responses[path]()) : Promise.reject(new Error(`inattendu : ${url}`))
  })
  vi.stubGlobal('fetch', fetchMock)
  const client = new QueryClient({ defaultOptions: { queries: { retry: false } } })
  render(
    <QueryClientProvider client={client}>
      <MemoryRouter initialEntries={['/']}>
        <Routes>
          <Route path="/" element={<HomePage />} />
          <Route path="/connexion" element={<LoginSpy />} />
        </Routes>
      </MemoryRouter>
    </QueryClientProvider>,
  )
  return fetchMock
}

afterEach(() => {
  vi.unstubAllGlobals()
})

describe('HomePage', () => {
  it("affiche la personne connectée et l'état du serveur", async () => {
    renderHome({
      '/auth/me': () => json(ME),
      '/health': () => json({ status: 'ok', database: 'reachable' }),
    })
    expect(await screen.findByRole('heading', { level: 1 })).toHaveTextContent('Connecté : Marie Joseph (B07-42)')
    expect(await screen.findByText('Le serveur et la base de données répondent.')).toBeInTheDocument()
  })

  it("renvoie vers la connexion quand personne n'est connecté", async () => {
    renderHome({ '/auth/me': () => json({ detail: "Vous n'êtes pas connecté." }, 401) })
    expect(await screen.findByText('Page de connexion')).toBeInTheDocument()
  })

  it('signale une session expirée en revenant à la connexion', async () => {
    renderHome({ '/auth/me': () => json({ detail: 'Votre session a expiré, reconnectez-vous.' }, 401) })
    expect(await screen.findByText('Page de connexion?expiree=1')).toBeInTheDocument()
  })

  it('se déconnecte et revient à la connexion', async () => {
    const fetchMock = renderHome({
      '/auth/me': () => json(ME),
      '/health': () => json({ status: 'ok', database: 'reachable' }),
      '/auth/logout': () => new Response(null, { status: 204 }),
    })
    await userEvent.setup().click(await screen.findByRole('button', { name: 'Se déconnecter' }))

    expect(await screen.findByText('Page de connexion')).toBeInTheDocument()
    expect(fetchMock.mock.calls.some(([url]) => String(url).endsWith('/auth/logout'))).toBe(true)
  })
})
