import { screen, within } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { AccountPage } from '../../src/pages/account'
import { NewAccountPage } from '../../src/pages/account-new'
import { AccountsPage } from '../../src/pages/accounts'
import { json, me, renderApp } from './renderApp'

function account(overrides: Record<string, unknown> = {}) {
  return {
    id: 'u-1', badge: 'B07-42', first_name: 'Marie', last_name: 'Joseph', email: 'marie@example.test',
    phone: null, roles: ['secretary'], is_active: true, is_blocked: false, has_password: true,
    created_at: '2026-11-17T10:00:00Z', ...overrides,
  }
}

const HISTORY = [
  { occurred_at: '2026-11-17T10:00:00Z', actor_user_id: null, actor_label: 'Ligne de commande (administrateur)', table_name: 'users', action: 'create', before: null, after: { badge: 'B07-42' } },
  { occurred_at: '2026-11-17T10:00:00Z', actor_user_id: null, actor_label: 'Ligne de commande (administrateur)', table_name: 'user_roles', action: 'create', before: null, after: { role: 'secretary' } },
]

afterEach(() => {
  vi.unstubAllGlobals()
})

describe('AccountsPage', () => {
  it('liste les comptes par nom, avec rôles et statuts', async () => {
    renderApp(<AccountsPage />, {
      at: '/comptes', path: '/comptes',
      responses: {
        '/auth/me': () => json(me(['coordinator'])),
        '/users': () => json([
          account(),
          account({ id: 'u-2', badge: 'C03-15', first_name: 'Paul', last_name: 'Michel', roles: ['trainer'], has_password: false }),
          account({ id: 'u-3', badge: 'A01-01', first_name: 'Ada', last_name: 'Admin', roles: ['it_admin'], is_blocked: true }),
        ]),
      },
    })
    const table = await screen.findByRole('table')
    const rows = within(table).getAllByRole('row').slice(1).map((row) => row.textContent)
    expect(rows).toEqual([
      'A01-01AdminAdaAdministrateur informatiqueBloqué',
      'B07-42JosephMarieSecrétaireActif',
      'C03-15MichelPaulFormateurEn attente du mot de passe',
    ])
    expect(screen.getByRole('link', { name: 'Nouveau compte' })).toHaveAttribute('href', '/comptes/nouveau')
  })

  it("refuse l'écran à un formateur", async () => {
    renderApp(<AccountsPage />, { at: '/comptes', path: '/comptes', responses: { '/auth/me': () => json(me(['trainer'])) } })
    expect(await screen.findByText("Vous n'avez pas accès à cette page.")).toBeInTheDocument()
  })
})

describe('NewAccountPage', () => {
  it("ne propose pas « Administrateur informatique » au coordonnateur", async () => {
    renderApp(<NewAccountPage />, { at: '/comptes/nouveau', path: '/comptes/nouveau', responses: { '/auth/me': () => json(me(['coordinator'])) } })
    await screen.findByRole('heading', { name: 'Nouveau compte' })
    expect(screen.queryByLabelText('Administrateur informatique')).not.toBeInTheDocument()
    expect(screen.getByLabelText('Formateur')).toBeInTheDocument()
  })

  it("crée un compte et dit où le lien est parti", async () => {
    const fetchMock = renderApp(<NewAccountPage />, {
      at: '/comptes/nouveau', path: '/comptes/nouveau',
      responses: { '/auth/me': () => json(me(['it_admin'])), '/users': () => json(account({ has_password: false }), 201) },
    })
    const user = userEvent.setup()
    await user.type(await screen.findByLabelText('Numéro de badge'), 'b07-42')
    await user.type(screen.getByLabelText('Prénom'), 'Marie')
    await user.type(screen.getByLabelText('Nom'), 'Joseph')
    await user.type(screen.getByLabelText('Email'), 'marie@example.test')
    expect(screen.getByRole('button', { name: 'Créer le compte' })).toBeDisabled()
    await user.click(screen.getByLabelText('Secrétaire'))
    await user.click(screen.getByLabelText('Administrateur informatique'))
    await user.click(screen.getByRole('button', { name: 'Créer le compte' }))

    expect(await screen.findByRole('status')).toHaveTextContent(
      'Compte créé : un lien pour choisir le mot de passe a été envoyé à marie@example.test.',
    )
    const call = fetchMock.mock.calls.find(([url]) => String(url).endsWith('/users')) as unknown as [string, RequestInit]
    expect(JSON.parse(call[1].body as string)).toEqual({
      badge: 'b07-42', first_name: 'Marie', last_name: 'Joseph', email: 'marie@example.test', phone: null,
      roles: ['secretary', 'it_admin'],
    })
    expect(screen.getByRole('link', { name: 'Ouvrir le compte' })).toHaveAttribute('href', '/comptes/B07-42')
  })

  it('affiche le refus du serveur en français', async () => {
    renderApp(<NewAccountPage />, {
      at: '/comptes/nouveau', path: '/comptes/nouveau',
      responses: { '/auth/me': () => json(me(['it_admin'])), '/users': () => json({ detail: 'Ce numéro de badge est déjà utilisé.' }, 409) },
    })
    const user = userEvent.setup()
    await user.type(await screen.findByLabelText('Numéro de badge'), 'B07-42')
    await user.type(screen.getByLabelText('Prénom'), 'Marie')
    await user.type(screen.getByLabelText('Nom'), 'Joseph')
    await user.type(screen.getByLabelText('Email'), 'marie@example.test')
    await user.click(screen.getByLabelText('Secrétaire'))
    await user.click(screen.getByRole('button', { name: 'Créer le compte' }))
    expect(await screen.findByRole('alert')).toHaveTextContent('Ce numéro de badge est déjà utilisé.')
  })
})

describe('AccountPage', () => {
  function renderAccount(roles: string[], extra: Record<string, () => Response> = {}, accountOverrides = {}) {
    return renderApp(<AccountPage />, {
      at: '/comptes/B07-42', path: '/comptes/:badge',
      responses: {
        '/auth/me': () => json(me(roles)),
        '/users/by-badge/B07-42': () => json(account(accountOverrides)),
        '/history/users/u-1': () => json(HISTORY),
        '/users': () => json([account()]),
        ...extra,
      },
    })
  }

  it('montre le compte et son historique en phrases', async () => {
    renderAccount(['coordinator'])
    expect(await screen.findByRole('heading', { name: 'Marie Joseph' })).toBeInTheDocument()
    expect(screen.getByRole('heading', { name: 'Historique' })).toBeInTheDocument()
    expect(await screen.findByText('Compte créé (B07-42)')).toBeInTheDocument()
    expect(screen.getByText('Rôle ajouté : Secrétaire')).toBeInTheDocument()
  })

  it("ne montre aucune action au coordonnateur", async () => {
    renderAccount(['coordinator'])
    await screen.findByRole('heading', { name: 'Marie Joseph' })
    expect(screen.queryByRole('button', { name: 'Désactiver' })).not.toBeInTheDocument()
    expect(screen.queryByRole('button', { name: 'Modifier les rôles' })).not.toBeInTheDocument()
  })

  it("demande confirmation avant de désactiver, puis désactive", async () => {
    const fetchMock = renderAccount(['it_admin'], {
      '/users/u-1/deactivate': () => json(account({ is_active: false })),
    })
    const user = userEvent.setup()
    await user.click(await screen.findByRole('button', { name: 'Désactiver' }))
    const dialog = screen.getByRole('dialog')
    expect(within(dialog).getByText('Désactiver le compte de Marie Joseph ?')).toBeInTheDocument()
    expect(fetchMock.mock.calls.some(([url]) => String(url).endsWith('/deactivate'))).toBe(false)

    await user.click(within(dialog).getByRole('button', { name: 'Désactiver' }))
    expect(fetchMock.mock.calls.some(([url]) => String(url).endsWith('/deactivate'))).toBe(true)
  })

  it("propose « Débloquer » seulement pour un compte bloqué", async () => {
    renderAccount(['it_admin'], {}, { is_blocked: true })
    expect(await screen.findByRole('button', { name: 'Débloquer' })).toBeInTheDocument()
  })

  it("affiche le refus du dernier administrateur en français", async () => {
    renderAccount(['it_admin'], {
      '/users/u-1/deactivate': () =>
        json({ detail: "C'est le dernier administrateur actif : l'application ne peut pas rester sans administrateur." }, 409),
    })
    const user = userEvent.setup()
    await user.click(await screen.findByRole('button', { name: 'Désactiver' }))
    await user.click(within(screen.getByRole('dialog')).getByRole('button', { name: 'Désactiver' }))
    expect(await within(screen.getByRole('dialog')).findByRole('alert')).toHaveTextContent('dernier administrateur actif')
  })

  it("modifie les rôles après confirmation", async () => {
    const fetchMock = renderAccount(['it_admin'], {
      '/users/u-1/roles': () => json(account({ roles: ['trainer'] })),
    })
    const user = userEvent.setup()
    await user.click(await screen.findByRole('button', { name: 'Modifier les rôles' }))
    const dialog = screen.getByRole('dialog')
    await user.click(within(dialog).getByLabelText('Secrétaire'))
    await user.click(within(dialog).getByLabelText('Formateur'))
    await user.click(within(dialog).getByRole('button', { name: 'Enregistrer les rôles' }))

    const call = fetchMock.mock.calls.find(([url]) => String(url).endsWith('/roles')) as unknown as [string, RequestInit]
    expect(call[1].method).toBe('PUT')
    expect(JSON.parse(call[1].body as string)).toEqual({ roles: ['trainer'] })
  })
})
