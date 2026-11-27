import { screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { RequestPage } from '../../src/pages/request'
import { NewRequestPage } from '../../src/pages/request-new'
import { RequestsPage } from '../../src/pages/requests'
import { json, me, renderApp } from './renderApp'

function request(overrides: Record<string, unknown> = {}) {
  return {
    id: 'r-1', requesting_service: 'Service de sûreté', is_external: false, received_on: '2026-11-20',
    training_id: 't-1', training_title: 'Conduite sur la rampe', expected_participants: 12, desired_period: 'mars 2027',
    comment: null, status: 'pending', decided_by_name: null, decided_at: null, decision_reason: null,
    recorded_by_name: 'Sonia Saintil (S02-02)', created_at: '2026-11-24T15:00:00Z', ...overrides,
  }
}

const TRAININGS = [
  { id: 't-1', title: 'Conduite sur la rampe', description: null, subdomain_id: 's', subdomain_name: 'Conduite sur la rampe', domain_id: 'd', domain_name: 'Sûreté-Sécurité', created_at: '' },
]

afterEach(() => {
  vi.unstubAllGlobals()
})

function calls(fetchMock: ReturnType<typeof renderApp>) {
  return fetchMock.mock.calls as unknown as [string, RequestInit | undefined][]
}

describe('RequestsPage', () => {
  it('montre les demandes en attente par défaut', async () => {
    const fetchMock = renderApp(<RequestsPage />, {
      at: '/demandes', path: '/demandes',
      responses: { '/auth/me': () => json(me(['direction'])), '/training-requests?status=pending': () => json([request()]) },
    })
    expect(await screen.findByRole('link', { name: '20/11/2026' })).toHaveAttribute('href', '/demandes/r-1')
    expect(screen.getAllByText('En attente').length).toBeGreaterThan(0)
    expect(screen.queryByRole('link', { name: 'Nouvelle demande' })).not.toBeInTheDocument()
    expect(calls(fetchMock).some(([url]) => url.endsWith('/training-requests?status=pending'))).toBe(true)
  })

  it('refuse le formateur', async () => {
    renderApp(<RequestsPage />, { at: '/demandes', path: '/demandes', responses: { '/auth/me': () => json(me(['trainer'])) } })
    expect(await screen.findByText("Vous n'avez pas accès à cette page.")).toBeInTheDocument()
  })
})

describe('NewRequestPage', () => {
  it('envoie la demande et propose « Nouvelle formation »', async () => {
    const fetchMock = renderApp(<NewRequestPage />, {
      at: '/demandes/nouvelle', path: '/demandes/nouvelle',
      responses: {
        '/auth/me': () => json(me(['secretary'])),
        '/trainings': () => json(TRAININGS),
        '/training-requests': () => json({ detail: 'Le nombre de participants prévu doit aller de 1 à 500.' }, 422),
      },
    })
    expect(await screen.findByRole('link', { name: 'Nouvelle formation' })).toHaveAttribute('href', '/formations/nouvelle')
    await userEvent.type(screen.getByLabelText('Service demandeur'), 'Service de sûreté')
    await userEvent.click(screen.getByLabelText('Entreprise externe'))
    await screen.findByRole('option', { name: 'Conduite sur la rampe' })
    await userEvent.selectOptions(screen.getByLabelText('Formation demandée'), 't-1')
    await userEvent.type(screen.getByLabelText('Nombre de participants prévu'), '700')
    await userEvent.click(screen.getByRole('button', { name: 'Enregistrer la demande' }))
    expect(await screen.findByRole('alert')).toHaveTextContent('de 1 à 500')
    const body = JSON.parse(String(calls(fetchMock).find(([url, init]) => url.endsWith('/training-requests') && init?.method === 'POST')?.[1]?.body))
    expect(body).toMatchObject({ requesting_service: 'Service de sûreté', is_external: true, training_id: 't-1', expected_participants: 700 })
    expect(body.received_on).toMatch(/^\d{4}-\d{2}-\d{2}$/)
  })
})

describe('RequestPage', () => {
  function page(roles: string[], overrides: Record<string, unknown> = {}, extra: Record<string, () => Response> = {}) {
    return renderApp(<RequestPage />, {
      at: '/demandes/r-1', path: '/demandes/:id',
      responses: {
        '/auth/me': () => json(me(roles)),
        '/training-requests/r-1': () => json(request(overrides)),
        '/history/training_requests/r-1': () => json([]),
        '/trainings': () => json(TRAININGS),
        ...extra,
      },
    })
  }

  it('ne laisse pas le chef de service décider ni ajuster', async () => {
    page(['service_head'])
    await screen.findByRole('heading', { name: 'Service de sûreté' })
    expect(screen.queryByRole('button', { name: 'Valider ou refuser' })).not.toBeInTheDocument()
    expect(screen.queryByRole('button', { name: 'Modifier' })).not.toBeInTheDocument()
  })

  it('laisse le coordonnateur refuser avec un motif', async () => {
    const fetchMock = page(['coordinator'], {}, { '/training-requests/r-1/decision': () => json(request({ status: 'refused' })) })
    await userEvent.click(await screen.findByRole('button', { name: 'Valider ou refuser' }))
    await userEvent.click(screen.getByLabelText('Refuser'))
    await userEvent.type(screen.getByLabelText('Motif'), 'Pas de formateur')
    await userEvent.click(screen.getByRole('button', { name: 'Enregistrer la décision' }))
    const call = calls(fetchMock).find(([url]) => url.endsWith('/decision'))
    expect(JSON.parse(String(call?.[1]?.body))).toEqual({ status: 'refused', reason: 'Pas de formateur' })
  })

  it('ne propose pas au coordonnateur de revenir sur une décision, mais le laisse ajuster', async () => {
    page(['coordinator'], { status: 'approved', decided_by_name: 'Rose Pierre (E05-55)' })
    await screen.findByText('Rose Pierre (E05-55)')
    expect(screen.queryByRole('button', { name: /Corriger la décision|Valider ou refuser/ })).not.toBeInTheDocument()
    expect(screen.getByRole('button', { name: 'Modifier' })).toBeInTheDocument()
  })

  it("donne « Corriger la décision » à l'administrateur", async () => {
    page(['it_admin'], { status: 'approved', decided_by_name: 'Rose Pierre (E05-55)' })
    expect(await screen.findByRole('button', { name: 'Corriger la décision' })).toBeInTheDocument()
  })
})
