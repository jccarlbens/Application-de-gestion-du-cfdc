import { useQuery } from '@tanstack/react-query'
import { useState } from 'react'
import { Link } from 'react-router-dom'
import {
  RequestStatusBadge,
  STATUS_LABELS,
  fetchTrainingRequests,
  formatDate,
  type RequestStatus,
} from '../../../entities/training-request'
import { canRecordTraining, canSeeCatalogue, type Viewer } from '../../../entities/viewer'
import { ApiError } from '../../../shared/api'
import { AccessDenied } from '../../../shared/ui'
import { AppShell } from '../../../widgets/app-shell'

function RequestList({ viewer }: { viewer: Viewer }) {
  const [status, setStatus] = useState<RequestStatus | ''>('pending')
  const requests = useQuery({ queryKey: ['training-requests', status], queryFn: () => fetchTrainingRequests(status) })

  return (
    <>
      <div className="mb-6 flex flex-wrap items-center justify-between gap-3">
        <h1 className="text-lg font-semibold text-brand-900">Demandes de formation</h1>
        {canRecordTraining(viewer.roles) && (
          <Link
            to="/demandes/nouvelle"
            className="rounded-md bg-brand-700 px-4 py-2 text-sm font-medium text-white hover:bg-brand-600"
          >
            Nouvelle demande
          </Link>
        )}
      </div>
      <label className="mb-6 block max-w-xs text-sm font-medium text-brand-900">
        Statut
        <select
          className="mt-1 w-full rounded-md border border-brand-100 px-3 py-2"
          value={status}
          onChange={(event) => setStatus(event.target.value as RequestStatus | '')}
        >
          {(Object.keys(STATUS_LABELS) as RequestStatus[]).map((s) => (
            <option key={s} value={s}>
              {STATUS_LABELS[s]}
            </option>
          ))}
          <option value="">Toutes</option>
        </select>
      </label>
      {requests.isPending && <p className="text-brand-900">Chargement des demandes…</p>}
      {requests.isError && (
        <p role="alert" className="font-medium text-red-700">
          {requests.error instanceof ApiError ? requests.error.message : 'Le serveur ne répond pas.'}
        </p>
      )}
      {requests.data && requests.data.length === 0 && <p className="text-brand-900">Aucune demande avec ce statut.</p>}
      {requests.data && requests.data.length > 0 && (
        <>
          <table className="hidden w-full border-collapse text-left text-sm md:table">
            <thead>
              <tr className="border-b border-brand-100 text-brand-900">
                <th className="py-2 pr-4 font-semibold">Reçue le</th>
                <th className="py-2 pr-4 font-semibold">Service demandeur</th>
                <th className="py-2 pr-4 font-semibold">Formation</th>
                <th className="py-2 pr-4 font-semibold">Participants</th>
                <th className="py-2 font-semibold">Statut</th>
              </tr>
            </thead>
            <tbody>
              {requests.data.map((r) => (
                <tr key={r.id} className="border-b border-brand-50 hover:bg-brand-50">
                  <td className="py-2 pr-4">
                    <Link to={`/demandes/${r.id}`} className="font-medium text-brand-700 underline">
                      {formatDate(r.receivedOn)}
                    </Link>
                  </td>
                  <td className="py-2 pr-4">
                    {r.requestingService}
                    {r.isExternal && <span className="ml-1 text-xs text-brand-700">(externe)</span>}
                  </td>
                  <td className="py-2 pr-4">{r.trainingTitle}</td>
                  <td className="py-2 pr-4">{r.expectedParticipants}</td>
                  <td className="py-2">
                    <RequestStatusBadge status={r.status} />
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
          <ul className="space-y-3 md:hidden" aria-label="Demandes">
            {requests.data.map((r) => (
              <li key={r.id}>
                <Link to={`/demandes/${r.id}`} className="block rounded-md border border-brand-100 p-4 hover:border-brand-600">
                  <span className="flex items-center justify-between gap-2">
                    <span className="font-semibold text-brand-900">{r.requestingService}</span>
                    <RequestStatusBadge status={r.status} />
                  </span>
                  <span className="block text-sm text-brand-900">{r.trainingTitle}</span>
                  <span className="block text-sm text-brand-700">
                    Reçue le {formatDate(r.receivedOn)} · {r.expectedParticipants} participants
                  </span>
                </Link>
              </li>
            ))}
          </ul>
        </>
      )}
    </>
  )
}

export function RequestsPage() {
  return (
    <AppShell>
      {(viewer) =>
        canSeeCatalogue(viewer.roles) ? (
          <div className="max-w-5xl">
            <RequestList viewer={viewer} />
          </div>
        ) : (
          <AccessDenied />
        )
      }
    </AppShell>
  )
}
