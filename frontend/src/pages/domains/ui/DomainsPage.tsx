import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { useState, type FormEvent } from 'react'
import { Link } from 'react-router-dom'
import { HistoryPanel, type SubjectType } from '../../../entities/history'
import { addDomain, addSubdomain, fetchDomains, renameDomain, renameSubdomain } from '../../../entities/training'
import { isAdmin } from '../../../entities/viewer'
import { ApiError } from '../../../shared/api'
import { AccessDenied } from '../../../shared/ui'
import { AppShell } from '../../../widgets/app-shell'

const inputClass =
  'w-full rounded-md border border-brand-100 px-3 py-2 focus:border-brand-600 focus:outline-none focus:ring-2 focus:ring-brand-100'
const smallButton = 'rounded-md border border-brand-100 px-3 py-1.5 text-sm font-medium text-brand-900 hover:bg-brand-50'

function errorText(error: unknown): string | null {
  if (!error) return null
  return error instanceof ApiError ? error.message : 'Le serveur ne répond pas.'
}

/** Un champ et un bouton : ajouter un nom, ou en remplacer un. */
function NameForm({
  label,
  initial = '',
  submitLabel,
  onSubmit,
  onCancel,
}: {
  label: string
  initial?: string
  submitLabel: string
  onSubmit: (name: string) => Promise<unknown>
  onCancel?: () => void
}) {
  const queryClient = useQueryClient()
  const [name, setName] = useState(initial)
  const mutation = useMutation({
    mutationFn: () => onSubmit(name),
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: ['domains'] })
      void queryClient.invalidateQueries({ queryKey: ['trainings'] })
      void queryClient.invalidateQueries({ queryKey: ['history'] })
      setName('')
      onCancel?.()
    },
  })

  function submit(event: FormEvent) {
    event.preventDefault()
    mutation.mutate()
  }

  const error = errorText(mutation.error)
  return (
    <form onSubmit={submit} noValidate className="mt-2">
      <div className="flex flex-wrap items-end gap-2">
        <label className="min-w-48 flex-1 text-sm font-medium text-brand-900">
          {label}
          <input
            className={`mt-1 ${inputClass}`}
            maxLength={100}
            value={name}
            onChange={(event) => {
              setName(event.target.value)
              mutation.reset()
            }}
          />
        </label>
        <button type="submit" disabled={!name.trim() || mutation.isPending} className={`${smallButton} disabled:opacity-60`}>
          {submitLabel}
        </button>
        {onCancel && (
          <button type="button" onClick={onCancel} className={smallButton}>
            Annuler
          </button>
        )}
      </div>
      {error && (
        <p role="alert" className="mt-1 text-sm font-medium text-red-700">
          {error}
        </p>
      )}
    </form>
  )
}

/** Un domaine ou un sous-domaine : son nom, « Renommer » et son historique. */
function NamedItem({
  kind,
  subjectType,
  id,
  name,
  onRename,
  level,
}: {
  kind: string
  subjectType: SubjectType
  id: string
  name: string
  onRename: (name: string) => Promise<unknown>
  level: 'domain' | 'subdomain'
}) {
  const [renaming, setRenaming] = useState(false)
  const [showHistory, setShowHistory] = useState(false)
  const Title = level === 'domain' ? 'h2' : 'span'
  return (
    <div>
      <div className="flex flex-wrap items-center gap-2">
        <Title className={level === 'domain' ? 'text-base font-semibold text-brand-900' : 'text-brand-900'}>{name}</Title>
        <button type="button" className="text-sm text-brand-700 underline" onClick={() => setRenaming(!renaming)}>
          Renommer
        </button>
        <button
          type="button"
          className="text-sm text-brand-700 underline"
          aria-expanded={showHistory}
          onClick={() => setShowHistory(!showHistory)}
        >
          Historique
        </button>
      </div>
      {renaming && (
        <NameForm
          label={`Nouveau nom du ${kind}`}
          initial={name}
          submitLabel="Renommer"
          onSubmit={onRename}
          onCancel={() => setRenaming(false)}
        />
      )}
      {showHistory && (
        <HistoryPanel
          subjectType={subjectType}
          subjectId={id}
          headingLevel={3}
          emptyText="Chargé à l'installation : pas d'entrée au journal."
        />
      )}
    </div>
  )
}

function DomainList() {
  const domains = useQuery({ queryKey: ['domains'], queryFn: fetchDomains })
  if (domains.isPending) return <p className="text-brand-900">Chargement…</p>
  if (domains.isError) return <p className="font-medium text-red-700">{errorText(domains.error)}</p>

  return (
    <>
      <ul className="space-y-6">
        {domains.data.map((domain) => (
          <li key={domain.id} className="rounded-md border border-brand-100 p-4">
            <NamedItem
              kind="domaine"
              subjectType="domains"
              id={domain.id}
              name={domain.name}
              level="domain"
              onRename={(name) => renameDomain(domain.id, name)}
            />
            <ul className="mt-3 space-y-2 border-l-2 border-brand-50 pl-4">
              {domain.subdomains.map((sub) => (
                <li key={sub.id}>
                  <NamedItem
                    kind="sous-domaine"
                    subjectType="subdomains"
                    id={sub.id}
                    name={sub.name}
                    level="subdomain"
                    onRename={(name) => renameSubdomain(sub.id, name)}
                  />
                </li>
              ))}
            </ul>
            <NameForm
              label={`Nouveau sous-domaine de « ${domain.name} »`}
              submitLabel="Ajouter"
              onSubmit={(name) => addSubdomain(domain.id, name)}
            />
          </li>
        ))}
      </ul>
      <div className="mt-8">
        <NameForm label="Nouveau domaine" submitLabel="Ajouter le domaine" onSubmit={addDomain} />
      </div>
    </>
  )
}

export function DomainsPage() {
  return (
    <AppShell>
      {(viewer) =>
        isAdmin(viewer.roles) ? (
          <div className="max-w-3xl">
            <p className="mb-2 text-sm">
              <Link to="/formations" className="text-brand-700 underline">
                Formations
              </Link>
            </p>
            <h1 className="mb-2 text-lg font-semibold text-brand-900">Domaines et sous-domaines</h1>
            <p className="mb-6 text-sm text-brand-900">Rien ne se supprime : on ajoute, ou on renomme.</p>
            <DomainList />
          </div>
        ) : (
          <AccessDenied />
        )
      }
    </AppShell>
  )
}
