import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { render, screen } from '@testing-library/react'
import { HomePage } from '../../src/pages/home'

function renderWithResponse(response: Response | Error) {
  vi.stubGlobal(
    'fetch',
    vi.fn(() => (response instanceof Error ? Promise.reject(response) : Promise.resolve(response))),
  )
  const client = new QueryClient({ defaultOptions: { queries: { retry: false } } })
  render(
    <QueryClientProvider client={client}>
      <HomePage />
    </QueryClientProvider>,
  )
}

afterEach(() => {
  vi.unstubAllGlobals()
})

describe('HomePage', () => {
  it("affiche le nom de l'application en français", () => {
    renderWithResponse(new Response(JSON.stringify({ status: 'ok', database: 'reachable' })))
    expect(screen.getByRole('heading', { level: 1 })).toHaveTextContent('CFDC — Gestion des formations')
  })

  it('dit quand le serveur et la base répondent', async () => {
    renderWithResponse(new Response(JSON.stringify({ status: 'ok', database: 'reachable' })))
    expect(await screen.findByText('Le serveur et la base de données répondent.')).toBeInTheDocument()
  })

  it('dit quand la base est injoignable', async () => {
    renderWithResponse(new Response(JSON.stringify({ status: 'ok', database: 'unreachable' })))
    expect(
      await screen.findByText('Le serveur répond, mais la base de données est injoignable.'),
    ).toBeInTheDocument()
  })

  it('dit quand le serveur ne répond pas', async () => {
    renderWithResponse(new Error('réseau coupé'))
    expect(await screen.findByText('Le serveur ne répond pas.')).toBeInTheDocument()
  })
})
