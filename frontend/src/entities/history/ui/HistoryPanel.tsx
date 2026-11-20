import { useQuery } from '@tanstack/react-query'
import { useState } from 'react'
import { fetchHistory } from '../api/history'
import { describeEntry, formatWhen } from '../lib/describeEntry'
import { authorOf, type HistoryEntry, type SubjectType } from '../model/history'

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

/** Le panneau « Historique » d'une fiche : son journal, en phrases. L'auteur
 *  est nommé par le serveur (US-010, décision 4A). `emptyText` dit pourquoi
 *  une fiche n'a aucune entrée (créée avant le journal, chargée à l'installation). */
export function HistoryPanel({
  subjectType,
  subjectId,
  emptyText,
  headingLevel = 2,
  names = {},
}: {
  subjectType: SubjectType
  subjectId: string
  emptyText: string
  headingLevel?: 2 | 3
  /** Les noms connus de l'écran (un formateur…), pour des phrases complètes. */
  names?: Readonly<Record<string, string>>
}) {
  const history = useQuery({
    queryKey: ['history', subjectType, subjectId],
    queryFn: () => fetchHistory(subjectType, subjectId),
  })
  const Heading = headingLevel === 2 ? 'h2' : 'h3'
  const headingId = `historique-${subjectId}`

  return (
    <section aria-labelledby={headingId} className="mt-8">
      <Heading id={headingId} className="mb-3 font-semibold text-brand-900">
        Historique
      </Heading>
      {history.isPending && <p className="text-brand-900">Chargement…</p>}
      {history.isError && <p className="text-red-700">L'historique n'a pas pu être chargé.</p>}
      {history.data && history.data.length === 0 && <p className="text-brand-900">{emptyText}</p>}
      {history.data && history.data.length > 0 && (
        <ol className="space-y-2">
          {history.data.map((entry, index) => {
            const description = describeEntry(entry, names)
            return (
              <li key={index} className="rounded-md border border-brand-50 px-3 py-2 text-sm">
                <span className="text-brand-700">{formatWhen(entry.occurredAt)}</span>
                {' — '}
                <span className="font-medium text-brand-900">{authorOf(entry)}</span>
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
