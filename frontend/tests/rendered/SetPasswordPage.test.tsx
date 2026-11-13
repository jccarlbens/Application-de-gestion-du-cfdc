import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { MemoryRouter } from 'react-router-dom'
import { SetPasswordPage } from '../../src/pages/set-password'

function renderAt(url: string, response?: Response) {
  const fetchMock = vi.fn(() => Promise.resolve(response ?? new Response(null, { status: 204 })))
  vi.stubGlobal('fetch', fetchMock)
  const client = new QueryClient({ defaultOptions: { mutations: { retry: false } } })
  render(
    <QueryClientProvider client={client}>
      <MemoryRouter initialEntries={[url]}>
        <SetPasswordPage />
      </MemoryRouter>
    </QueryClientProvider>,
  )
  return fetchMock
}

async function fill(password: string, confirmation = password) {
  const user = userEvent.setup()
  await user.type(screen.getByLabelText('Mot de passe'), password)
  await user.type(screen.getByLabelText('Confirmez le mot de passe'), confirmation)
  await user.click(screen.getByRole('button', { name: 'Enregistrer mon mot de passe' }))
}

afterEach(() => {
  vi.unstubAllGlobals()
})

describe('SetPasswordPage', () => {
  it('envoie le jeton du lien et le mot de passe, puis confirme', async () => {
    const fetchMock = renderAt('/mot-de-passe?jeton=abc123')
    await fill('formation2026')

    expect(await screen.findByText('Mot de passe enregistré')).toBeInTheDocument()
    const [url, init] = fetchMock.mock.calls[0] as unknown as [string, RequestInit]
    expect(url).toBe('/api/v1/password/setup')
    expect(JSON.parse(init.body as string)).toEqual({ token: 'abc123', password: 'formation2026' })
  })

  it("refuse un mot de passe trop faible sans appeler le serveur", async () => {
    const fetchMock = renderAt('/mot-de-passe?jeton=abc123')
    await fill('court')

    expect(screen.getByRole('alert')).toHaveTextContent('au moins 8 caractères')
    expect(fetchMock).not.toHaveBeenCalled()
  })

  it('affiche le message du serveur quand le lien a expiré', async () => {
    const expired = new Response(JSON.stringify({ detail: "Ce lien n'est plus valable : il a expiré ou a déjà servi." }), {
      status: 410,
    })
    renderAt('/mot-de-passe?jeton=abc123', expired)
    await fill('formation2026')

    expect(await screen.findByRole('alert')).toHaveTextContent("Ce lien n'est plus valable")
  })

  it('dit quand le lien ne contient pas de jeton', () => {
    renderAt('/mot-de-passe')
    expect(screen.getByText('Lien incomplet')).toBeInTheDocument()
  })
})
