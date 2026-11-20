// Fichier d'aide aux tests : le rechargement à chaud de Vite ne le concerne pas.
// oxlint-disable react/only-export-components
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { render } from '@testing-library/react'
import type { ReactNode } from 'react'
import { MemoryRouter, Route, Routes, useLocation } from 'react-router-dom'

export function json(body: unknown, status = 200): Response {
  return new Response(JSON.stringify(body), { status })
}

export function me(roles: string[]) {
  return { badge: 'B07-42', first_name: 'Marie', last_name: 'Joseph', roles }
}

function LoginSpy() {
  const location = useLocation()
  return <p>Page de connexion{location.search}</p>
}

/** Rend une page à une adresse, avec de fausses réponses de l'API par chemin. */
export function renderApp(
  page: ReactNode,
  { at = '/', path = '/', responses }: { at?: string; path?: string; responses: Record<string, () => Response> },
) {
  const fetchMock = vi.fn((url: string) => {
    // Le chemin le plus long qui convient : « /history/trainings/t-1 » ne doit
    // pas recevoir la réponse de « /trainings/t-1 ».
    const key = Object.keys(responses)
      .filter((p) => String(url).endsWith(p))
      .sort((a, b) => b.length - a.length)[0]
    return key ? Promise.resolve(responses[key]()) : Promise.reject(new Error(`inattendu : ${url}`))
  })
  vi.stubGlobal('fetch', fetchMock)
  const client = new QueryClient({ defaultOptions: { queries: { retry: false } } })
  render(
    <QueryClientProvider client={client}>
      <MemoryRouter initialEntries={[at]}>
        <Routes>
          <Route path={path} element={page} />
          <Route path="/connexion" element={<LoginSpy />} />
          <Route path="*" element={<p>Autre page</p>} />
        </Routes>
      </MemoryRouter>
    </QueryClientProvider>,
  )
  return fetchMock
}
