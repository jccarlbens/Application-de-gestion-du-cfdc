import { useQuery } from '@tanstack/react-query'
import { Link } from 'react-router-dom'
import type { TrainingRequest } from '../../../entities/training-request'
import { SessionList, fetchTrainingSessions } from '../../../entities/training-session'
import { canPlanSession, type Viewer } from '../../../entities/viewer'

/** Les sessions qui répondent à une demande (US-015) ; on ne planifie que
 *  pour une demande validée. */
export function RequestSessions({ request, viewer }: { request: TrainingRequest; viewer: Viewer }) {
  const sessions = useQuery({ queryKey: ['training-sessions', 'request', request.id], queryFn: () => fetchTrainingSessions({ requestId: request.id }) })
  return (
    <section aria-labelledby="sessions" className="mt-8">
      <div className="mb-3 flex flex-wrap items-center justify-between gap-3">
        <h2 id="sessions" className="font-semibold text-brand-900">Sessions</h2>
        {canPlanSession(viewer.roles) && request.status === 'approved' && (
          <Link to={`/sessions/nouvelle?demande=${request.id}`} className="rounded-md border border-brand-100 px-4 py-2 text-sm font-medium text-brand-900 hover:bg-brand-50">
            Planifier une session
          </Link>
        )}
      </div>
      {sessions.data && sessions.data.length === 0 && (
        <p className="text-brand-900">
          {request.status === 'approved' ? "Aucune session pour l'instant." : 'Une session se planifie une fois la demande validée.'}
        </p>
      )}
      {sessions.data && sessions.data.length > 0 && <SessionList sessions={sessions.data} />}
    </section>
  )
}
