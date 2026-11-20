import { screen, within } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { DomainsPage } from '../../src/pages/domains'
import { TrainingPage } from '../../src/pages/training'
import { NewTrainingPage } from '../../src/pages/training-new'
import { TrainingsPage } from '../../src/pages/trainings'
import { json, me, renderApp } from './renderApp'

const DOMAINS = [
  { id: 'd-acc', name: 'Accueil', subdomains: [{ id: 's-pro', domain_id: 'd-acc', name: 'Protocole' }] },
  { id: 'd-sur', name: 'Sûreté-Sécurité', subdomains: [{ id: 's-ram', domain_id: 'd-sur', name: 'Conduite sur la rampe' }] },
]

function training(overrides: Record<string, unknown> = {}) {
  return {
    id: 't-1', title: 'Conduite sur la rampe', description: null, subdomain_id: 's-ram',
    subdomain_name: 'Conduite sur la rampe', domain_id: 'd-sur', domain_name: 'Sûreté-Sécurité',
    created_at: '2026-11-20T10:00:00Z', ...overrides,
  }
}

const HISTORY = [
  {
    occurred_at: '2026-11-20T10:00:00Z', actor_user_id: 'u-9', actor_label: 'Utilisateur connecté',
    actor_name: 'Marie Joseph (B07-42)', table_name: 'trainings', action: 'create', before: null,
    after: { title: 'Conduite sur la rampe' },
  },
]

afterEach(() => {
  vi.unstubAllGlobals()
})

describe('TrainingsPage', () => {
  it('regroupe le catalogue et ne montre pas les boutons à la direction', async () => {
    renderApp(<TrainingsPage />, {
      at: '/formations', path: '/formations',
      responses: {
        '/auth/me': () => json(me(['direction'])),
        '/trainings': () => json([training(), training({ id: 't-2', title: 'Accueil VIP', subdomain_id: 's-pro', subdomain_name: 'Protocole', domain_id: 'd-acc', domain_name: 'Accueil' })]),
        '/domains': () => json(DOMAINS),
      },
    })
    const headings = await screen.findAllByRole('heading', { level: 2 })
    expect(headings.map((h) => h.textContent)).toEqual(['Accueil', 'Sûreté-Sécurité'])
    expect(screen.getByRole('link', { name: 'Accueil VIP' })).toHaveAttribute('href', '/formations/t-2')
    expect(screen.queryByRole('link', { name: 'Nouvelle formation' })).not.toBeInTheDocument()
    expect(screen.queryByRole('link', { name: 'Domaines et sous-domaines' })).not.toBeInTheDocument()
  })

  it('filtre par domaine', async () => {
    renderApp(<TrainingsPage />, {
      at: '/formations', path: '/formations',
      responses: {
        '/auth/me': () => json(me(['secretary'])),
        '/trainings': () => json([training(), training({ id: 't-2', title: 'Accueil VIP', subdomain_id: 's-pro', subdomain_name: 'Protocole', domain_id: 'd-acc', domain_name: 'Accueil' })]),
        '/domains': () => json(DOMAINS),
      },
    })
    await screen.findByRole('link', { name: 'Accueil VIP' })
    await screen.findByRole('option', { name: 'Accueil' })
    await userEvent.selectOptions(screen.getByLabelText('Domaine'), 'd-sur')
    expect(screen.queryByRole('link', { name: 'Accueil VIP' })).not.toBeInTheDocument()
    expect(screen.getByRole('link', { name: 'Conduite sur la rampe' })).toBeInTheDocument()
    expect(screen.getByRole('link', { name: 'Nouvelle formation' })).toBeInTheDocument()
  })

  it("montre « Domaines et sous-domaines » à l'administrateur seul", async () => {
    renderApp(<TrainingsPage />, {
      at: '/formations', path: '/formations',
      responses: { '/auth/me': () => json(me(['it_admin'])), '/trainings': () => json([]), '/domains': () => json(DOMAINS) },
    })
    expect(await screen.findByRole('link', { name: 'Domaines et sous-domaines' })).toHaveAttribute('href', '/formations/domaines')
    expect(screen.getByText('Aucune formation enregistrée pour l’instant.')).toBeInTheDocument()
  })

  it('refuse le catalogue au formateur', async () => {
    renderApp(<TrainingsPage />, { at: '/formations', path: '/formations', responses: { '/auth/me': () => json(me(['trainer'])) } })
    expect(await screen.findByText("Vous n'avez pas accès à cette page.")).toBeInTheDocument()
  })
})

describe('NewTrainingPage', () => {
  it('affiche le refus du serveur en français', async () => {
    const fetchMock = renderApp(<NewTrainingPage />, {
      at: '/formations/nouvelle', path: '/formations/nouvelle',
      responses: {
        '/auth/me': () => json(me(['secretary'])),
        '/domains': () => json(DOMAINS),
        '/trainings': () => json({ detail: 'Une formation porte déjà cet intitulé.' }, 409),
      },
    })
    await userEvent.type(await screen.findByLabelText('Intitulé'), 'Protocole')
    await screen.findByRole('option', { name: 'Protocole' })
    await userEvent.selectOptions(screen.getByLabelText('Sous-domaine'), 's-pro')
    await userEvent.click(screen.getByRole('button', { name: 'Enregistrer la formation' }))
    expect(await screen.findByRole('alert')).toHaveTextContent('Une formation porte déjà cet intitulé.')
    const calls = fetchMock.mock.calls as unknown as [string, RequestInit | undefined][]
    const call = calls.find(([url]) => String(url).endsWith('/trainings'))
    expect(JSON.parse(String(call?.[1]?.body))).toEqual({ title: 'Protocole', description: null, subdomain_id: 's-pro' })
  })

  it("n'est pas ouverte à la direction", async () => {
    renderApp(<NewTrainingPage />, { at: '/formations/nouvelle', path: '/formations/nouvelle', responses: { '/auth/me': () => json(me(['direction'])) } })
    expect(await screen.findByText("Vous n'avez pas accès à cette page.")).toBeInTheDocument()
  })
})

describe('TrainingPage', () => {
  it("montre la fiche et l'historique nommé, sans « Modifier » pour la secrétaire", async () => {
    renderApp(<TrainingPage />, {
      at: '/formations/t-1', path: '/formations/:id',
      responses: {
        '/auth/me': () => json(me(['secretary'])),
        '/trainings/t-1': () => json(training()),
        '/history/trainings/t-1': () => json(HISTORY),
      },
    })
    expect(await screen.findByRole('heading', { name: 'Conduite sur la rampe' })).toBeInTheDocument()
    expect(screen.getByText('Sûreté-Sécurité › Conduite sur la rampe')).toBeInTheDocument()
    expect(await screen.findByText('Marie Joseph (B07-42)')).toBeInTheDocument()
    expect(screen.getByText('Formation créée : « Conduite sur la rampe »')).toBeInTheDocument()
    expect(screen.queryByRole('button', { name: 'Modifier' })).not.toBeInTheDocument()
  })

  it("laisse l'administrateur modifier la formation", async () => {
    const fetchMock = renderApp(<TrainingPage />, {
      at: '/formations/t-1', path: '/formations/:id',
      responses: {
        '/auth/me': () => json(me(['it_admin'])),
        '/trainings/t-1': () => json(training()),
        '/history/trainings/t-1': () => json(HISTORY),
        '/domains': () => json(DOMAINS),
      },
    })
    await userEvent.click(await screen.findByRole('button', { name: 'Modifier' }))
    const title = screen.getByLabelText('Intitulé')
    await userEvent.clear(title)
    await userEvent.type(title, 'Conduite sur la rampe — niveau 1')
    await userEvent.click(screen.getByRole('button', { name: 'Enregistrer les modifications' }))
    const calls = fetchMock.mock.calls as unknown as [string, RequestInit | undefined][]
    const call = calls.find(([, init]) => init?.method === 'PUT')
    expect(String(call?.[0])).toMatch(/\/trainings\/t-1$/)
    expect(JSON.parse(String(call?.[1]?.body)).title).toBe('Conduite sur la rampe — niveau 1')
  })
})

describe('DomainsPage', () => {
  it("liste les domaines et dit d'où vient la liste de départ", async () => {
    renderApp(<DomainsPage />, {
      at: '/formations/domaines', path: '/formations/domaines',
      responses: {
        '/auth/me': () => json(me(['it_admin'])),
        '/domains': () => json(DOMAINS),
        '/history/subdomains/s-pro': () => json([]),
      },
    })
    const accueil = (await screen.findByRole('heading', { name: 'Accueil' })).closest('li') as HTMLElement
    const protocol = within(accueil).getByText('Protocole').parentElement as HTMLElement
    await userEvent.click(within(protocol).getByRole('button', { name: 'Historique' }))
    expect(await screen.findByText("Chargé à l'installation : pas d'entrée au journal.")).toBeInTheDocument()
    expect(within(accueil).getByLabelText('Nouveau sous-domaine de « Accueil »')).toBeInTheDocument()
  })

  it("n'est ouverte qu'à l'administrateur", async () => {
    renderApp(<DomainsPage />, { at: '/formations/domaines', path: '/formations/domaines', responses: { '/auth/me': () => json(me(['coordinator'])) } })
    expect(await screen.findByText("Vous n'avez pas accès à cette page.")).toBeInTheDocument()
  })
})
