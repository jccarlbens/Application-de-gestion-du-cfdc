import { useQuery } from '@tanstack/react-query'
import { Link } from 'react-router-dom'
import { SessionList, fetchTrainingSessions } from '../../../entities/training-session'
import { canPlanSession, canSeeCatalogue, type Viewer } from '../../../entities/viewer'
import { ApiError } from '../../../shared/api'
import { AccessDenied } from '../../../shared/ui'
import { AppShell } from '../../../widgets/app-shell'

/** « Sessions et calendrier » : une liste, à venir d'abord, en attendant le
 *  calendrier de US-017 (US-015, décision 7A). */
function Sessions({ viewer }: { viewer: Viewer }) {
  const sessions = useQuery({ queryKey: ['training-sessions', 'all'], queryFn: () => fetchTrainingSessions() })
  return (
    <>
      <div className="mb-6 flex flex-wrap items-center justify-between gap-3">
        <h1 className="text-lg font-semibold text-brand-900">Sessions</h1>
        {canPlanSession(viewer.roles) && (
          <Link to="/sessions/nouvelle" className="rounded-md bg-brand-700 px-4 py-2 text-sm font-medium text-white hover:bg-brand-600">
            Planifier une session
          </Link>
        )}
      </div>
      <p className="mb-4 text-sm text-brand-700">Les sessions à venir d'abord, puis les sessions passées. Le calendrier arrive bientôt.</p>
      {sessions.isPending && <p className="text-brand-900">Chargement des sessions…</p>}
      {sessions.isError && (
        <p role="alert" className="font-medium text-red-700">
          {sessions.error instanceof ApiError ? sessions.error.message : 'Le serveur ne répond pas.'}
        </p>
      )}
      {sessions.data && sessions.data.length === 0 && <p className="text-brand-900">Aucune session pour l'instant.</p>}
      {sessions.data && sessions.data.length > 0 && <SessionList sessions={sessions.data} showTraining />}
    </>
  )
}

export function SessionsPage() {
  return (
    <AppShell>
      {(viewer) =>
        canSeeCatalogue(viewer.roles) ? (
          <div className="max-w-4xl">
            <Sessions viewer={viewer} />
          </div>
        ) : (
          <AccessDenied />
        )
      }
    </AppShell>
  )
}
