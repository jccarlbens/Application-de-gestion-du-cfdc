import { useQuery } from '@tanstack/react-query'
import { useState } from 'react'
import {
  describeEntry,
  fetchAccountHistory,
  fetchAccounts,
  formatWhen,
  type HistoryEntry,
} from '../../../entities/account'

function Details({ entry }: { entry: HistoryEntry }) {
  const [open, setOpen] = useState(false)
  return (
    <>
      <button
        type="button"
        onClick={() => setOpen(!open)}
        aria-expanded={open}
        className="ml-2 text-sm text-brand-700 underline"
      >
        Détails
      </button>
      {open && (
        <div className="mt-2 grid gap-2 text-xs sm:grid-cols-2">
          <pre className="overflow-x-auto rounded-md bg-gray-50 p-2">Avant : {JSON.stringify(entry.before, null, 2)}</pre>
          <pre className="overflow-x-auto rounded-md bg-gray-50 p-2">Après : {JSON.stringify(entry.after, null, 2)}</pre>
        </div>
      )}
    </>
  )
}

/** Le panneau « Historique » d'un compte : son journal, en phrases (US-009). */
export function AccountHistory({ accountId }: { accountId: string }) {
  const history = useQuery({ queryKey: ['account-history', accountId], queryFn: () => fetchAccountHistory(accountId) })
  // Pour nommer l'auteur quand c'est une personne connectée.
  const accounts = useQuery({ queryKey: ['accounts'], queryFn: fetchAccounts })

  function author(entry: HistoryEntry): string {
    const person = accounts.data?.find((account) => account.id === entry.actorUserId)
    return person ? `${person.firstName} ${person.lastName} (${person.badge})` : entry.actorLabel
  }

  return (
    <section aria-labelledby="historique" className="mt-8">
      <h2 id="historique" className="mb-3 font-semibold text-brand-900">
        Historique
      </h2>
      {history.isPending && <p className="text-brand-900">Chargement…</p>}
      {history.isError && <p className="text-red-700">L'historique n'a pas pu être chargé.</p>}
      {history.data && history.data.length === 0 && (
        <p className="text-brand-900">
          Aucune entrée : ce compte a été créé avant la mise en place du journal.
        </p>
      )}
      {history.data && history.data.length > 0 && (
        <ol className="space-y-2">
          {history.data.map((entry, index) => {
            const description = describeEntry(entry)
            return (
              <li key={index} className="rounded-md border border-brand-50 px-3 py-2 text-sm">
                <span className="text-brand-700">{formatWhen(entry.occurredAt)}</span>
                {' — '}
                <span className="font-medium text-brand-900">{author(entry)}</span>
                {' : '}
                <span className="text-brand-900">{description.text}</span>
                {description.needsDetails && <Details entry={entry} />}
              </li>
            )
          })}
        </ol>
      )}
    </section>
  )
}
