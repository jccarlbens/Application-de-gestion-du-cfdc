import { useMutation, useQueryClient } from '@tanstack/react-query'
import { useState, type FormEvent } from 'react'
import { Link } from 'react-router-dom'
import { createAccount, type Account } from '../../../entities/account'
import { ROLE_LABELS, canManageAccounts, grantableRoles, type Role, type Viewer } from '../../../entities/viewer'
import { ApiError } from '../../../shared/api'
import { AccessDenied } from '../../../shared/ui'
import { AppShell } from '../../../widgets/app-shell'

const inputClass =
  'mt-1 w-full rounded-md border border-brand-100 px-3 py-2 focus:border-brand-600 focus:outline-none focus:ring-2 focus:ring-brand-100'

const EMPTY = { badge: '', firstName: '', lastName: '', email: '', phone: '' }

function NewAccountForm({ viewer }: { viewer: Viewer }) {
  const queryClient = useQueryClient()
  const [fields, setFields] = useState(EMPTY)
  const [roles, setRoles] = useState<Role[]>([])
  const [created, setCreated] = useState<Account | null>(null)
  const mutation = useMutation({
    mutationFn: () => createAccount({ ...fields, roles }),
    onSuccess: (account) => {
      setCreated(account)
      void queryClient.invalidateQueries({ queryKey: ['accounts'] })
    },
  })

  if (created) {
    return (
      <div className="rounded-md border border-brand-100 bg-brand-50 p-6">
        <p role="status" className="mb-4 font-medium text-brand-900">
          Compte créé : un lien pour choisir le mot de passe a été envoyé à {created.email}.
        </p>
        <div className="flex flex-wrap gap-3">
          <Link
            to={`/comptes/${created.badge}`}
            className="rounded-md bg-brand-700 px-4 py-2 text-sm font-medium text-white hover:bg-brand-600"
          >
            Ouvrir le compte
          </Link>
          <button
            type="button"
            onClick={() => {
              setCreated(null)
              setFields(EMPTY)
              setRoles([])
              mutation.reset()
            }}
            className="rounded-md border border-brand-100 px-4 py-2 text-sm font-medium text-brand-900 hover:bg-white"
          >
            Créer un autre compte
          </button>
        </div>
      </div>
    )
  }

  function field(name: keyof typeof EMPTY) {
    return {
      value: fields[name],
      onChange: (event: { target: { value: string } }) => {
        setFields({ ...fields, [name]: event.target.value })
        mutation.reset()
      },
    }
  }

  function toggle(role: Role) {
    setRoles((current) => (current.includes(role) ? current.filter((r) => r !== role) : [...current, role]))
    mutation.reset()
  }

  function submit(event: FormEvent) {
    event.preventDefault()
    mutation.mutate()
  }

  const complete = Boolean(fields.badge && fields.firstName && fields.lastName && fields.email && roles.length)
  const error =
    mutation.error instanceof ApiError ? mutation.error.message : mutation.error ? 'Le serveur ne répond pas.' : null

  return (
    <form onSubmit={submit} noValidate className="space-y-4">
      <label className="block text-sm font-medium text-brand-900">
        Numéro de badge
        <input className={inputClass} placeholder="A00-00" {...field('badge')} />
      </label>
      <div className="grid gap-4 sm:grid-cols-2">
        <label className="block text-sm font-medium text-brand-900">
          Prénom
          <input className={inputClass} autoComplete="off" {...field('firstName')} />
        </label>
        <label className="block text-sm font-medium text-brand-900">
          Nom
          <input className={inputClass} autoComplete="off" {...field('lastName')} />
        </label>
      </div>
      <label className="block text-sm font-medium text-brand-900">
        Email
        <input type="email" className={inputClass} autoComplete="off" {...field('email')} />
      </label>
      <label className="block text-sm font-medium text-brand-900">
        Téléphone <span className="font-normal">(facultatif)</span>
        <input type="tel" className={inputClass} autoComplete="off" {...field('phone')} />
      </label>
      <fieldset>
        <legend className="text-sm font-medium text-brand-900">Rôles</legend>
        <div className="mt-2 grid gap-2 sm:grid-cols-2">
          {grantableRoles(viewer.roles).map((role) => (
            <label key={role} className="flex items-center gap-2 text-sm text-brand-900">
              <input type="checkbox" checked={roles.includes(role)} onChange={() => toggle(role)} />
              {ROLE_LABELS[role]}
            </label>
          ))}
        </div>
      </fieldset>
      {error && (
        <p role="alert" className="text-sm font-medium text-red-700">
          {error}
        </p>
      )}
      <div className="flex flex-wrap gap-3">
        <button
          type="submit"
          disabled={!complete || mutation.isPending}
          className="rounded-md bg-brand-700 px-4 py-2 font-medium text-white hover:bg-brand-600 disabled:opacity-60"
        >
          {mutation.isPending ? 'Création…' : 'Créer le compte'}
        </button>
        <Link to="/comptes" className="rounded-md border border-brand-100 px-4 py-2 font-medium text-brand-900">
          Annuler
        </Link>
      </div>
    </form>
  )
}

export function NewAccountPage() {
  return (
    <AppShell>
      {(viewer) =>
        canManageAccounts(viewer.roles) ? (
          <div className="max-w-xl">
            <h1 className="mb-6 text-lg font-semibold text-brand-900">Nouveau compte</h1>
            <NewAccountForm viewer={viewer} />
          </div>
        ) : (
          <AccessDenied />
        )
      }
    </AppShell>
  )
}
