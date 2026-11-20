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
        '/trainings/t-1/modules': () => json([]),
        '/trainers': () => json([]),
        '/trainings/t-1/documents': () => json([]),
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
        '/trainings/t-1/modules': () => json([]),
        '/trainers': () => json([]),
        '/trainings/t-1/documents': () => json([]),
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

const PAUL = { id: 'p', first_name: 'Paul', last_name: 'Michel', badge: 'C03-15', is_active: true, is_trainer: true }
const ROSE = { id: 'r', first_name: 'Rose', last_name: 'Pierre', badge: 'E05-55', is_active: true, is_trainer: true }

function module(overrides: Record<string, unknown> = {}) {
  return { id: 'm-1', training_id: 't-1', title: 'Vitesses', description: null, trainer: null, created_at: '2026-11-20T10:00:00Z', ...overrides }
}

function trainingPage(roles: string[], modules: unknown[], extra: Record<string, () => Response> = {}) {
  return renderApp(<TrainingPage />, {
    at: '/formations/t-1', path: '/formations/:id',
    responses: {
      '/auth/me': () => json(me(roles)),
      '/trainings/t-1': () => json(training()),
      '/history/trainings/t-1': () => json([]),
      '/trainings/t-1/modules': () => json(modules),
      '/trainers': () => json([PAUL, ROSE]),
      '/trainings/t-1/documents': () => json([]),
      ...extra,
    },
  })
}

describe('Les modules sur la fiche', () => {
  it("dit qu'il n'y a pas encore de module", async () => {
    trainingPage(['direction'], [])
    expect(await screen.findByText("Aucun module pour l'instant.")).toBeInTheDocument()
    expect(screen.queryByRole('button', { name: 'Ajouter un module' })).not.toBeInTheDocument()
  })

  it('liste les modules avec leur formateur et signale un compte désactivé', async () => {
    trainingPage(['direction'], [
      module(),
      module({ id: 'm-2', title: 'Balisage', trainer: { ...PAUL, is_active: false } }),
    ])
    expect(await screen.findByText('Formateur à désigner')).toBeInTheDocument()
    expect(screen.getByText('Paul Michel (C03-15) (compte désactivé)')).toBeInTheDocument()
    expect(screen.queryByRole('button', { name: 'Désigner le formateur' })).not.toBeInTheDocument()
  })

  it('laisse la secrétaire ajouter un module avec son formateur', async () => {
    const fetchMock = trainingPage(['secretary'], [], { '/trainings/t-1/modules': () => json([]) })
    await userEvent.click(await screen.findByRole('button', { name: 'Ajouter un module' }))
    await userEvent.type(screen.getByLabelText('Titre du module'), 'Vitesses')
    await screen.findByRole('option', { name: 'Paul Michel (C03-15)' })
    await userEvent.selectOptions(screen.getByLabelText('Formateur'), 'p')
    await userEvent.click(screen.getByRole('button', { name: 'Enregistrer le module' }))
    const calls = fetchMock.mock.calls as unknown as [string, RequestInit | undefined][]
    const call = calls.find(([url, init]) => String(url).endsWith('/trainings/t-1/modules') && init?.method === 'POST')
    expect(JSON.parse(String(call?.[1]?.body))).toEqual({ title: 'Vitesses', description: null, trainer_id: 'p' })
  })

  it("laisse la secrétaire désigner le formateur d'un module « à désigner », mais pas changer un formateur", async () => {
    const fetchMock = trainingPage(['secretary'], [module(), module({ id: 'm-2', title: 'Balisage', trainer: ROSE })], {
      '/modules/m-1/trainer': () => json(module({ trainer: PAUL })),
    })
    const buttons = await screen.findAllByRole('button', { name: 'Désigner le formateur' })
    expect(buttons).toHaveLength(1)
    expect(screen.queryByRole('button', { name: /Modifier le module/ })).not.toBeInTheDocument()
    await userEvent.click(buttons[0])
    await screen.findAllByRole('option', { name: 'Paul Michel (C03-15)' })
    await userEvent.selectOptions(screen.getByLabelText('Formateur de « Vitesses »'), 'p')
    await userEvent.click(screen.getByRole('button', { name: 'Désigner' }))
    const calls = fetchMock.mock.calls as unknown as [string, RequestInit | undefined][]
    const call = calls.find(([url]) => String(url).endsWith('/modules/m-1/trainer'))
    expect(JSON.parse(String(call?.[1]?.body))).toEqual({ trainer_id: 'p' })
  })

  it("affiche le refus du serveur en français", async () => {
    trainingPage(['secretary'], [], {
      '/trainings/t-1/modules': () => json([]),
    })
    await userEvent.click(await screen.findByRole('button', { name: 'Ajouter un module' }))
    vi.stubGlobal('fetch', vi.fn(() => Promise.resolve(json({ detail: 'Cette formation a déjà un module de ce titre.' }, 409))))
    await userEvent.type(screen.getByLabelText('Titre du module'), 'Vitesses')
    await userEvent.click(screen.getByRole('button', { name: 'Enregistrer le module' }))
    expect(await screen.findByRole('alert')).toHaveTextContent('Cette formation a déjà un module de ce titre.')
  })

  it("donne « Modifier » à l'administrateur, qui garde le formateur désactivé dans la liste", async () => {
    // Le serveur ne propose que les formateurs actifs : Paul n'est pas dans la liste.
    trainingPage(['it_admin'], [module({ trainer: { ...PAUL, is_active: false } })], { '/trainers': () => json([ROSE]) })
    await userEvent.click(await screen.findByRole('button', { name: 'Modifier le module « Vitesses »' }))
    const select = screen.getByLabelText('Formateur') as HTMLSelectElement
    expect(select.value).toBe('p')
    expect(screen.getByRole('option', { name: 'Paul Michel (C03-15) (compte désactivé)' })).toBeInTheDocument()
  })
})

function doc(overrides: Record<string, unknown> = {}) {
  return {
    id: 'd-1', module_id: 'm-1', module_title: 'Vitesses', training_id: 't-1', training_title: 'Conduite sur la rampe',
    file_name: 'Cours.pdf', content_type: 'application/pdf', size_bytes: 2.4 * 1024 * 1024,
    uploaded_by_name: 'Ada Admin (Z01-01)', uploaded_at: '2026-11-20T10:00:00Z', replaced_by_id: null, ...overrides,
  }
}

describe('Les documents de cours sur la fiche', () => {
  it('montre la liste à la secrétaire, sans lien ni bouton', async () => {
    trainingPage(['secretary'], [module({ trainer: PAUL })], { '/trainings/t-1/documents': () => json([doc()]) })
    expect(await screen.findByText('Cours.pdf')).toBeInTheDocument()
    expect(screen.getByText('2,4 Mo · 20/11/2026 · Ada Admin (Z01-01)')).toBeInTheDocument()
    expect(screen.queryByRole('link', { name: 'Cours.pdf' })).not.toBeInTheDocument()
    expect(screen.queryByText('Déposer un document')).not.toBeInTheDocument()
    expect(screen.queryByText(/Remplacer/)).not.toBeInTheDocument()
  })

  it("donne à l'administrateur le lien, « Remplacer » et les versions remplacées", async () => {
    trainingPage(['it_admin'], [module({ trainer: PAUL })], {
      '/trainings/t-1/documents': () => json([doc({ id: 'd-0', file_name: 'Ancien.pdf', replaced_by_id: 'd-1' }), doc()]),
    })
    expect(await screen.findByRole('link', { name: 'Cours.pdf' })).toHaveAttribute('href', '/api/v1/documents/d-1/download')
    expect(screen.getByText('Remplacer « Cours.pdf »')).toBeInTheDocument()
    expect(screen.getByText('Versions remplacées (1)')).toBeInTheDocument()
    expect(screen.queryByText('Remplacer « Ancien.pdf »')).not.toBeInTheDocument()
  })

  it("envoie le fichier choisi par l'administrateur", async () => {
    const fetchMock = trainingPage(['it_admin'], [module({ trainer: PAUL })], {
      '/modules/m-1/documents': () => json(doc(), 201),
    })
    const file = new File(['%PDF-1.4'], 'Nouveau.pdf', { type: 'application/pdf' })
    await userEvent.upload(await screen.findByLabelText('Déposer un document'), file)
    const calls = fetchMock.mock.calls as unknown as [string, RequestInit | undefined][]
    const call = calls.find(([url]) => String(url).endsWith('/modules/m-1/documents'))
    expect(call?.[1]?.method).toBe('POST')
    const body = call?.[1]?.body
    expect(body instanceof FormData && body.get('file')).toBe(file)
  })

  it('refuse tout de suite un fichier de plus de 25 Mo', async () => {
    const fetchMock = trainingPage(['it_admin'], [module({ trainer: PAUL })])
    const big = new File(['x'], 'Gros.pdf', { type: 'application/pdf' })
    Object.defineProperty(big, 'size', { value: 26 * 1024 * 1024 })
    await userEvent.upload(await screen.findByLabelText('Déposer un document'), big)
    expect(await screen.findByRole('alert')).toHaveTextContent('Le fichier dépasse 25 Mo.')
    const calls = fetchMock.mock.calls as unknown as [string][]
    expect(calls.some(([url]) => String(url).endsWith('/modules/m-1/documents'))).toBe(false)
  })

  it('affiche le refus du serveur en français', async () => {
    trainingPage(['it_admin'], [module({ trainer: PAUL })], {
      '/modules/m-1/documents': () => json({ detail: 'Le contenu du fichier ne correspond pas à son extension (.pdf) : il n’est pas accepté.' }, 422),
    })
    await userEvent.upload(await screen.findByLabelText('Déposer un document'), new File(['MZ'], 'faux.pdf'))
    expect(await screen.findByRole('alert')).toHaveTextContent('ne correspond pas à son extension')
  })
})
