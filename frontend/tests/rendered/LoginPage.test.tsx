import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { MemoryRouter, Route, Routes } from 'react-router-dom'
import { LoginPage } from '../../src/pages/login'

function renderAt(url: string, response: Response) {
  const fetchMock = vi.fn(() => Promise.resolve(response))
  vi.stubGlobal('fetch', fetchMock)
  const client = new QueryClient({ defaultOptions: { mutations: { retry: false } } })
  render(
    <QueryClientProvider client={client}>
      <MemoryRouter initialEntries={[url]}>
        <Routes>
          <Route path="/connexion" element={<LoginPage />} />
          <Route path="/" element={<p>Accueil connecté</p>} />
        </Routes>
      </MemoryRouter>
    </QueryClientProvider>,
  )
  return fetchMock
}

async function fill(badge: string, password: string) {
  const user = userEvent.setup()
  await user.type(screen.getByLabelText('Numéro de badge'), badge)
  await user.type(screen.getByLabelText('Mot de passe'), password)
  await user.click(screen.getByRole('button', { name: 'Se connecter' }))
}

afterEach(() => {
  vi.unstubAllGlobals()
})

describe('LoginPage', () => {
  it("envoie le numéro de badge et le mot de passe, puis mène à l'accueil", async () => {
    const fetchMock = renderAt(
      '/connexion',
      new Response(JSON.stringify({ badge: 'B07-42', first_name: 'Marie', last_name: 'Joseph', roles: [] })),
    )
    await fill('b07-42', 'formation2026')

    expect(await screen.findByText('Accueil connecté')).toBeInTheDocument()
    const [url, init] = fetchMock.mock.calls[0] as unknown as [string, RequestInit]
    expect(url).toBe('/api/v1/auth/login')
    expect(JSON.parse(init.body as string)).toEqual({ badge: 'b07-42', password: 'formation2026' })
  })

  it('affiche le message générique du serveur', async () => {
    renderAt(
      '/connexion',
      new Response(JSON.stringify({ detail: 'Numéro de badge ou mot de passe incorrect.' }), { status: 401 }),
    )
    await fill('B07-42', 'mauvais')
    expect(await screen.findByRole('alert')).toHaveTextContent('Numéro de badge ou mot de passe incorrect.')
  })

  it('dit que la session a expiré quand on y revient', () => {
    renderAt('/connexion?expiree=1', new Response(null))
    expect(screen.getByText('Votre session a expiré, reconnectez-vous.')).toBeInTheDocument()
  })

  it('attend les deux champs avant de permettre la connexion', () => {
    renderAt('/connexion', new Response(null))
    expect(screen.getByRole('button', { name: 'Se connecter' })).toBeDisabled()
  })
})
