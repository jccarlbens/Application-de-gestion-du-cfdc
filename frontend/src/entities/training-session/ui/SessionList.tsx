import { Link } from 'react-router-dom'
import { formatPeriod, type TrainingSession } from '../model/trainingSession'
import { SessionStatusBadge } from './SessionStatusBadge'

/** Une liste de sessions, chacune vers sa fiche. `showTraining` : afficher la
 *  formation (la liste générale) ; inutile sur la fiche d'une formation. */
export function SessionList({ sessions, showTraining = false }: { sessions: readonly TrainingSession[]; showTraining?: boolean }) {
  return (
    <ul className="space-y-2">
      {sessions.map((s) => (
        <li key={s.id}>
          <Link to={`/sessions/${s.id}`} className="block rounded-md border border-brand-50 px-3 py-2 hover:border-brand-600">
            <span className="flex flex-wrap items-center justify-between gap-2">
              <span className="font-medium text-brand-900">
                {showTraining ? s.trainingTitle : formatPeriod(s.startsOn, s.endsOn)}
                {s.label && <span className="ml-2 text-sm font-normal text-brand-700">{s.label}</span>}
              </span>
              <SessionStatusBadge status={s.status} />
            </span>
            {showTraining && <span className="block text-sm text-brand-700">{formatPeriod(s.startsOn, s.endsOn)}</span>}
          </Link>
        </li>
      ))}
    </ul>
  )
}
