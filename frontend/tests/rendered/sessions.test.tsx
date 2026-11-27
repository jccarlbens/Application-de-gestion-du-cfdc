import { screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { SessionPage } from '../../src/pages/session'
import { NewSessionPage } from '../../src/pages/session-new'
import { SessionsPage } from '../../src/pages/sessions'
import { json, me, renderApp } from './renderApp'

function session(overrides: Record<string, unknown> = {}) {
  return {
    id: 's-1', training_id: 't-1', training_title: 'Conduite sur la rampe', request_id: 'r-1', request_service: 'Service de sûreté',
    label: 'Groupe A', starts_on: '2026-12-02', ends_on: '2026-12-05', status: 'planned', cancel_reason: null,
    planned_by_name: 'Rose Pierre (E05-55)', created_at: '2026-11-24T15:00:00Z', ...overrides,
  }
}

afterEach(() => {
  vi.unstubAllGlobals()
})

function calls(fetchMock: ReturnType<typeof renderApp>) {
  return fetchMock.mock.calls as unknown as [string, RequestInit | undefined][]
}

describe('SessionsPage', () => {
  it('liste les sessions et ne propose pas de planifier à la secrétaire', async () => {
    renderApp(<SessionsPage />, {
      at: '/sessions', path: '/sessions',
      responses: { '/auth/me': () => json(me(['secretary'])), '/training-sessions': () => json([session(), session({ id: 's-2', status: 'finished', label: null })]) },
    })
    expect(await screen.findAllByText('Conduite sur la rampe')).toHaveLength(2)
    expect(screen.getAllByText('du 2 au 5 décembre 2026')).toHaveLength(2)
    expect(screen.getByText('Groupe A')).toBeInTheDocument()
    expect(screen.getByText('Terminée')).toBeInTheDocument()
    expect(screen.queryByRole('link', { name: 'Planifier une session' })).not.toBeInTheDocument()
  })

  it('refuse le formateur', async () => {
    renderApp(<SessionsPage />, { at: '/sessions', path: '/sessions', responses: { '/auth/me': () => json(me(['trainer'])) } })
    expect(await screen.findByText("Vous n'avez pas accès à cette page.")).toBeInTheDocument()
  })
})

describe('NewSessionPage', () => {
  it('planifie depuis une demande : la formation est celle de la demande', async () => {
    const fetchMock = renderApp(<NewSessionPage />, {
      at: '/sessions/nouvelle?demande=r-1', path: '/sessions/nouvelle',
      responses: {
        '/auth/me': () => json(me(['coordinator'])),
        '/training-requests/r-1': () => json({
          id: 'r-1', requesting_service: 'Service de sûreté', is_external: false, received_on: '2026-11-20', training_id: 't-1',
          training_title: 'Conduite sur la rampe', expected_participants: 40, desired_period: null, comment: null, status: 'approved',
          decided_by_name: null, decided_at: null, decision_reason: null, recorded_by_name: 'X',
        }),
        '/training-sessions': () => json({ detail: 'La date de fin ne peut pas précéder la date de début.' }, 422),
      },
    })
    expect(await screen.findByText('Service de sûreté')).toBeInTheDocument()
    expect(screen.queryByLabelText('Formation')).not.toBeInTheDocument()
    await userEvent.type(screen.getByLabelText('Date de début'), '2026-12-05')
    await userEvent.type(screen.getByLabelText('Date de fin'), '2026-12-02')
    await userEvent.click(screen.getByRole('button', { name: 'Planifier la session' }))
    expect(await screen.findByRole('alert')).toHaveTextContent('précéder')
    const body = JSON.parse(String(calls(fetchMock).find(([url, init]) => url.endsWith('/training-sessions') && init?.method === 'POST')?.[1]?.body))
    expect(body).toEqual({ training_id: null, request_id: 'r-1', label: null, starts_on: '2026-12-05', ends_on: '2026-12-02' })
  })
})

describe('SessionPage', () => {
  function page(roles: string[], overrides: Record<string, unknown> = {}) {
    return renderApp(<SessionPage />, {
      at: '/sessions/s-1', path: '/sessions/:id',
      responses: {
        '/auth/me': () => json(me(roles)),
        '/training-sessions/s-1': () => json(session(overrides)),
        '/history/training_sessions/s-1': () => json([]),
      },
    })
  }

  it('montre la fiche sans bouton à la secrétaire', async () => {
    page(['secretary'])
    expect(await screen.findByText('du 2 au 5 décembre 2026')).toBeInTheDocument()
    expect(screen.getByRole('link', { name: 'la demande de Service de sûreté' })).toHaveAttribute('href', '/demandes/r-1')
    expect(screen.queryByRole('button', { name: 'Reporter' })).not.toBeInTheDocument()
  })

  it('laisse le coordonnateur reporter et annuler une session planifiée', async () => {
    page(['coordinator'])
    expect(await screen.findByRole('button', { name: 'Reporter' })).toBeInTheDocument()
    expect(screen.getByRole('button', { name: 'Annuler la session' })).toBeInTheDocument()
  })

  it('ne laisse pas le coordonnateur reporter une session terminée', async () => {
    page(['coordinator'], { status: 'finished' })
    await screen.findByRole('button', { name: 'Annuler la session' })
    expect(screen.queryByRole('button', { name: 'Reporter' })).not.toBeInTheDocument()
  })

  it("propose à l'administrateur de remettre une session annulée en « planifiée »", async () => {
    page(['it_admin'], { status: 'cancelled', cancel_reason: 'Formateur absent' })
    expect(await screen.findByText('Formateur absent')).toBeInTheDocument()
    expect(screen.getByRole('button', { name: 'Remettre en « planifiée »' })).toBeInTheDocument()
    expect(screen.queryByRole('button', { name: 'Reporter' })).not.toBeInTheDocument()
  })
})

describe('SessionPage, administrateur', () => {
  it('lui laisse reporter une session terminée', async () => {
    renderApp(<SessionPage />, {
      at: '/sessions/s-1', path: '/sessions/:id',
      responses: {
        '/auth/me': () => json(me(['it_admin'])),
        '/training-sessions/s-1': () => json(session({ status: 'finished' })),
        '/history/training_sessions/s-1': () => json([]),
      },
    })
    expect(await screen.findByRole('button', { name: 'Reporter' })).toBeInTheDocument()
  })
})
