import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { useState } from 'react'
import { Link, useParams } from 'react-router-dom'
import {
  StatusBadge,
  accountStatus,
  fetchAccount,
  runAccountAction,
  setAccountRoles,
  type Account,
  type AccountAction,
} from '../../../entities/account'
import { HistoryPanel } from '../../../entities/history'
import { ALL_ROLES, ROLE_LABELS, canManageAccounts, isAdmin, rolesLabel, type Role } from '../../../entities/viewer'
import { ApiError } from '../../../shared/api'
import { AccessDenied, ConfirmDialog } from '../../../shared/ui'
import { AppShell } from '../../../widgets/app-shell'

type Pending = { kind: 'action'; action: AccountAction } | { kind: 'roles' } | null

const ACTION_TEXT: Record<AccountAction, { button: string; title: (name: string) => string; danger: boolean }> = {
  deactivate: { button: 'Désactiver', title: (n) => `Désactiver le compte de ${n} ?`, danger: true },
  reactivate: { button: 'Réactiver', title: (n) => `Réactiver le compte de ${n} ?`, danger: false },
  unblock: { button: 'Débloquer', title: (n) => `Débloquer le compte de ${n} ?`, danger: false },
}

function errorText(error: unknown): string | null {
  if (!error) return null
  return error instanceof ApiError ? error.message : 'Le serveur ne répond pas.'
}

function AdminActions({ account }: { account: Account }) {
  const queryClient = useQueryClient()
  const [pending, setPending] = useState<Pending>(null)
  const [roles, setRoles] = useState<Role[]>(account.roles)
  const name = `${account.firstName} ${account.lastName}`

  const mutation = useMutation({
    mutationFn: () =>
      pending?.kind === 'roles' ? setAccountRoles(account.id, roles) : runAccountAction(account.id, (pending as { action: AccountAction }).action),
    onSuccess: () => {
      setPending(null)
      void queryClient.invalidateQueries({ queryKey: ['account', account.badge] })
      void queryClient.invalidateQueries({ queryKey: ['account-history', account.id] })
      void queryClient.invalidateQueries({ queryKey: ['accounts'] })
    },
  })

  function open(next: Pending) {
    mutation.reset()
    if (next?.kind === 'roles') setRoles(account.roles)
    setPending(next)
  }

  const actions: AccountAction[] = [account.isActive ? 'deactivate' : 'reactivate']
  if (account.isBlocked) actions.push('unblock')

  return (
    <div className="mt-6 flex flex-wrap gap-3">
      <button
        type="button"
        onClick={() => open({ kind: 'roles' })}
        className="rounded-md border border-brand-600 px-4 py-2 text-sm font-medium text-brand-700 hover:bg-brand-50"
      >
        Modifier les rôles
      </button>
      {actions.map((action) => (
        <button
          key={action}
          type="button"
          onClick={() => open({ kind: 'action', action })}
          className={`rounded-md px-4 py-2 text-sm font-medium ${
            ACTION_TEXT[action].danger
              ? 'border border-red-700 text-red-700 hover:bg-red-50'
              : 'border border-brand-600 text-brand-700 hover:bg-brand-50'
          }`}
        >
          {ACTION_TEXT[action].button}
        </button>
      ))}

      <ConfirmDialog
        open={pending?.kind === 'roles'}
        title={`Modifier les rôles de ${name}`}
        confirmLabel="Enregistrer les rôles"
        pending={mutation.isPending}
        error={errorText(mutation.error) ?? (roles.length === 0 ? 'Un compte a au moins un rôle.' : null)}
        onConfirm={() => roles.length > 0 && mutation.mutate()}
        onCancel={() => setPending(null)}
      >
        <fieldset>
          <legend className="sr-only">Rôles</legend>
          <div className="grid gap-2">
            {ALL_ROLES.map((role) => (
              <label key={role} className="flex items-center gap-2">
                <input
                  type="checkbox"
                  checked={roles.includes(role)}
                  onChange={() =>
                    setRoles((current) => (current.includes(role) ? current.filter((r) => r !== role) : [...current, role]))
                  }
                />
                {ROLE_LABELS[role]}
              </label>
            ))}
          </div>
        </fieldset>
      </ConfirmDialog>

      {pending?.kind === 'action' && (
        <ConfirmDialog
          open
          title={ACTION_TEXT[pending.action].title(name)}
          confirmLabel={ACTION_TEXT[pending.action].button}
          danger={ACTION_TEXT[pending.action].danger}
          pending={mutation.isPending}
          error={errorText(mutation.error)}
          onConfirm={() => mutation.mutate()}
          onCancel={() => setPending(null)}
        >
          {pending.action === 'deactivate' && 'Ses sessions ouvertes seront fermées. Le compte et son historique restent.'}
        </ConfirmDialog>
      )}
    </div>
  )
}

function AccountDetails({ badge, admin }: { badge: string; admin: boolean }) {
  const account = useQuery({ queryKey: ['account', badge], queryFn: () => fetchAccount(badge), retry: false })

  if (account.isPending) return <p className="text-brand-900">Chargement…</p>
  if (account.isError) {
    return (
      <p role="alert" className="font-medium text-red-700">
        {errorText(account.error)}
      </p>
    )
  }

  const a = account.data
  return (
    <>
      <div className="flex flex-wrap items-center gap-3">
        <h1 className="text-lg font-semibold text-brand-900">
          {a.firstName} {a.lastName}
        </h1>
        <StatusBadge status={accountStatus(a)} />
      </div>
      <dl className="mt-4 grid gap-x-6 gap-y-2 text-sm sm:grid-cols-[max-content_1fr]">
        <dt className="font-medium text-brand-900">Numéro de badge</dt>
        <dd>{a.badge}</dd>
        <dt className="font-medium text-brand-900">Email</dt>
        <dd>{a.email}</dd>
        <dt className="font-medium text-brand-900">Téléphone</dt>
        <dd>{a.phone ?? '—'}</dd>
        <dt className="font-medium text-brand-900">Rôles</dt>
        <dd>{rolesLabel(a.roles)}</dd>
      </dl>
      {admin && <AdminActions key={`${a.roles.join()}-${a.isActive}-${a.isBlocked}`} account={a} />}
      <HistoryPanel
        subjectType="users"
        subjectId={a.id}
        emptyText="Aucune entrée : ce compte a été créé avant la mise en place du journal."
      />
    </>
  )
}

export function AccountPage() {
  const { badge = '' } = useParams()
  return (
    <AppShell>
      {(viewer) =>
        canManageAccounts(viewer.roles) ? (
          <div className="max-w-3xl">
            <Link to="/comptes" className="mb-4 inline-block text-sm text-brand-700 underline">
              ← Tous les comptes
            </Link>
            <AccountDetails badge={badge} admin={isAdmin(viewer.roles)} />
          </div>
        ) : (
          <AccessDenied />
        )
      }
    </AppShell>
  )
}
