import { useQuery } from '@tanstack/react-query'
import { Link } from 'react-router-dom'
import { SessionList, fetchTrainingSessions } from '../../../entities/training-session'
import { canPlanSession, type Viewer } from '../../../entities/viewer'

/** Les sessions d'une formation, sur sa fiche (US-015). */
export function TrainingSessions({ trainingId, viewer }: { trainingId: string; viewer: Viewer }) {
  const sessions = useQuery({ queryKey: ['training-sessions', 'training', trainingId], queryFn: () => fetchTrainingSessions({ trainingId }) })
  return (
    <section aria-labelledby="sessions" className="mt-8">
      <div className="mb-3 flex flex-wrap items-center justify-between gap-3">
        <h2 id="sessions" className="font-semibold text-brand-900">Sessions</h2>
        {canPlanSession(viewer.roles) && (
          <Link to={`/sessions/nouvelle?formation=${trainingId}`} className="rounded-md border border-brand-100 px-4 py-2 text-sm font-medium text-brand-900 hover:bg-brand-50">
            Planifier une session
          </Link>
        )}
      </div>
      {sessions.data && sessions.data.length === 0 && <p className="text-brand-900">Aucune session pour l'instant.</p>}
      {sessions.data && sessions.data.length > 0 && <SessionList sessions={sessions.data} />}
    </section>
  )
}
