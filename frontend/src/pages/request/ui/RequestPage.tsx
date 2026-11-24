import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { useState, type FormEvent, type ReactNode } from 'react'
import { Link, useLocation, useParams } from 'react-router-dom'
import { HistoryPanel } from '../../../entities/history'
import { fetchTrainings, trainingOptions } from '../../../entities/training'
import {
  RequestFields,
  RequestStatusBadge,
  TEXT_MAX,
  adjustTrainingRequest,
  decideTrainingRequest,
  fetchTrainingRequest,
  formatDate,
  type TrainingRequest,
  type TrainingRequestInput,
} from '../../../entities/training-request'
import { canAdjustRequest, canDecideRequest, canSeeCatalogue, isAdmin, type Viewer } from '../../../entities/viewer'
import { ApiError } from '../../../shared/api'
import { AccessDenied } from '../../../shared/ui'
import { AppShell } from '../../../widgets/app-shell'

const primary = 'rounded-md bg-brand-700 px-4 py-2 text-sm font-medium text-white hover:bg-brand-600 disabled:opacity-60'
const secondary = 'rounded-md border border-brand-100 px-4 py-2 text-sm font-medium text-brand-900 hover:bg-brand-50'

function errorText(error: unknown): string | null {
  if (!error) return null
  return error instanceof ApiError ? error.message : 'Le serveur ne répond pas.'
}

function useRefresh(id: string) {
  const queryClient = useQueryClient()
  return (updated: TrainingRequest) => {
    queryClient.setQueryData(['training-request', id], updated)
    void queryClient.invalidateQueries({ queryKey: ['training-requests'] })
    void queryClient.invalidateQueries({ queryKey: ['history', 'training_requests', id] })
  }
}

/** Valider ou refuser ; l'administrateur corrige aussi une décision prise. */
function DecisionForm({ request, onDone }: { request: TrainingRequest; onDone: () => void }) {
  const refresh = useRefresh(request.id)
  const [status, setStatus] = useState<'approved' | 'refused'>(request.status === 'approved' ? 'refused' : 'approved')
  const [reason, setReason] = useState(request.decisionReason ?? '')
  const mutation = useMutation({
    mutationFn: () => decideTrainingRequest(request.id, status, reason),
    onSuccess: (updated) => {
      refresh(updated)
      onDone()
    },
  })

  function submit(event: FormEvent) {
    event.preventDefault()
    mutation.mutate()
  }

  const error = errorText(mutation.error)
  return (
    <form onSubmit={submit} noValidate className="mt-4 space-y-3 rounded-md border border-brand-100 p-4" aria-label="Décision">
      <fieldset>
        <legend className="text-sm font-medium text-brand-900">Décision</legend>
        <div className="mt-1 flex gap-4 text-sm text-brand-900">
          <label className="flex items-center gap-2">
            <input type="radio" name="decision" checked={status === 'approved'} onChange={() => setStatus('approved')} />
            Valider
          </label>
          <label className="flex items-center gap-2">
            <input type="radio" name="decision" checked={status === 'refused'} onChange={() => setStatus('refused')} />
            Refuser
          </label>
        </div>
      </fieldset>
      <label className="block text-sm font-medium text-brand-900">
        Motif {status === 'approved' && <span className="font-normal">(facultatif)</span>}
        <textarea
          className="mt-1 w-full rounded-md border border-brand-100 px-3 py-2"
          rows={2}
          maxLength={TEXT_MAX}
          value={reason}
          onChange={(event) => {
            setReason(event.target.value)
            mutation.reset()
          }}
        />
      </label>
      {error && (
        <p role="alert" className="text-sm font-medium text-red-700">
          {error}
        </p>
      )}
      <div className="flex flex-wrap gap-3">
        <button type="submit" disabled={mutation.isPending} className={primary}>
          Enregistrer la décision
        </button>
        <button type="button" onClick={onDone} className={secondary}>
          Annuler
        </button>
      </div>
    </form>
  )
}

function AdjustForm({ request, onDone }: { request: TrainingRequest; onDone: () => void }) {
  const refresh = useRefresh(request.id)
  const trainings = useQuery({ queryKey: ['trainings'], queryFn: fetchTrainings })
  const [value, setValue] = useState<TrainingRequestInput>({
    requestingService: request.requestingService,
    isExternal: request.isExternal,
    receivedOn: request.receivedOn,
    trainingId: request.trainingId,
    expectedParticipants: String(request.expectedParticipants),
    desiredPeriod: request.desiredPeriod ?? '',
    comment: request.comment ?? '',
  })
  const mutation = useMutation({
    mutationFn: () => adjustTrainingRequest(request.id, value),
    onSuccess: (updated) => {
      refresh(updated)
      onDone()
    },
  })

  function submit(event: FormEvent) {
    event.preventDefault()
    mutation.mutate()
  }

  const error = errorText(mutation.error)
  return (
    <form onSubmit={submit} noValidate className="mt-4 space-y-4 rounded-md border border-brand-100 p-4" aria-label="Ajuster la demande">
      <RequestFields
        value={value}
        trainings={trainingOptions(trainings.data ?? [])}
        canCreateTraining={false}
        onChange={(next) => {
          setValue(next)
          mutation.reset()
        }}
      />
      {error && (
        <p role="alert" className="text-sm font-medium text-red-700">
          {error}
        </p>
      )}
      <div className="flex flex-wrap gap-3">
        <button type="submit" disabled={mutation.isPending} className={primary}>
          Enregistrer les modifications
        </button>
        <button type="button" onClick={onDone} className={secondary}>
          Annuler
        </button>
      </div>
    </form>
  )
}

function Field({ label, children }: { label: string; children: ReactNode }) {
  return (
    <div>
      <dt className="text-sm font-medium text-brand-900">{label}</dt>
      <dd className="text-brand-900">{children}</dd>
    </div>
  )
}

function RequestDetails({ id, viewer }: { id: string; viewer: Viewer }) {
  const location = useLocation()
  const [mode, setMode] = useState<'view' | 'decide' | 'adjust'>('view')
  const request = useQuery({ queryKey: ['training-request', id], queryFn: () => fetchTrainingRequest(id) })

  if (request.isPending) return <p className="text-brand-900">Chargement…</p>
  if (request.isError) return <p role="alert" className="font-medium text-red-700">{errorText(request.error)}</p>

  const r = request.data
  const created = (location.state as { created?: boolean } | null)?.created
  const canDecide = canDecideRequest(viewer.roles) && (r.status === 'pending' || isAdmin(viewer.roles))
  return (
    <>
      <p className="mb-2 text-sm">
        <Link to="/demandes" className="text-brand-700 underline">
          Demandes de formation
        </Link>
      </p>
      {created && mode === 'view' && (
        <p role="status" className="mb-4 rounded-md bg-brand-50 px-3 py-2 font-medium text-brand-900">
          Demande enregistrée.
        </p>
      )}
      <div className="flex flex-wrap items-center gap-3">
        <h1 className="text-lg font-semibold text-brand-900">{r.requestingService}</h1>
        <RequestStatusBadge status={r.status} />
      </div>
      <dl className="mt-4 grid gap-3 sm:grid-cols-2">
        <Field label="Origine">{r.isExternal ? 'Entreprise externe' : "Service de l'AAN"}</Field>
        <Field label="Reçue le">{formatDate(r.receivedOn)}</Field>
        <Field label="Formation demandée">
          {canSeeCatalogue(viewer.roles) ? (
            <Link to={`/formations/${r.trainingId}`} className="text-brand-700 underline">
              {r.trainingTitle}
            </Link>
          ) : (
            r.trainingTitle
          )}
        </Field>
        <Field label="Nombre de participants prévu">{r.expectedParticipants}</Field>
        <Field label="Période souhaitée">{r.desiredPeriod ?? '—'}</Field>
        <Field label="Enregistrée par">{r.recordedByName}</Field>
        {r.comment && <Field label="Commentaire">{r.comment}</Field>}
        {r.status !== 'pending' && (
          <Field label="Décision">
            {r.decidedByName}
            {r.decisionReason && ` — ${r.decisionReason}`}
          </Field>
        )}
      </dl>
      {mode === 'view' && (canDecide || canAdjustRequest(viewer.roles)) && (
        <div className="mt-4 flex flex-wrap gap-3">
          {canDecide && (
            <button type="button" className={primary} onClick={() => setMode('decide')}>
              {r.status === 'pending' ? 'Valider ou refuser' : 'Corriger la décision'}
            </button>
          )}
          {canAdjustRequest(viewer.roles) && (
            <button type="button" className={secondary} onClick={() => setMode('adjust')}>
              Modifier
            </button>
          )}
        </div>
      )}
      {mode === 'decide' && <DecisionForm request={r} onDone={() => setMode('view')} />}
      {mode === 'adjust' && <AdjustForm request={r} onDone={() => setMode('view')} />}
      <HistoryPanel subjectType="training_requests" subjectId={r.id} emptyText="Aucune entrée au journal." />
    </>
  )
}

export function RequestPage() {
  const { id = '' } = useParams()
  return (
    <AppShell>
      {(viewer) =>
        canSeeCatalogue(viewer.roles) ? (
          <div className="max-w-3xl">
            <RequestDetails id={id} viewer={viewer} />
          </div>
        ) : (
          <AccessDenied />
        )
      }
    </AppShell>
  )
}
