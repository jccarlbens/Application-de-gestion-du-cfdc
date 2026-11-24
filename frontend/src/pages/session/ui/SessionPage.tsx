import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { useState, type FormEvent, type ReactNode } from 'react'
import { Link, useLocation, useParams } from 'react-router-dom'
import { HistoryPanel } from '../../../entities/history'
import {
  SessionStatusBadge,
  cancelTrainingSession,
  fetchTrainingSession,
  formatPeriod,
  rescheduleTrainingSession,
  restoreTrainingSession,
  type TrainingSession,
} from '../../../entities/training-session'
import { canPlanSession, canSeeCatalogue, isAdmin, type Viewer } from '../../../entities/viewer'
import { ApiError } from '../../../shared/api'
import { AccessDenied } from '../../../shared/ui'
import { AppShell } from '../../../widgets/app-shell'

const inputClass = 'mt-1 w-full rounded-md border border-brand-100 px-3 py-2'
const primary = 'rounded-md bg-brand-700 px-4 py-2 text-sm font-medium text-white hover:bg-brand-600 disabled:opacity-60'
const secondary = 'rounded-md border border-brand-100 px-4 py-2 text-sm font-medium text-brand-900 hover:bg-brand-50'

function errorText(error: unknown): string | null {
  if (!error) return null
  return error instanceof ApiError ? error.message : 'Le serveur ne répond pas.'
}

function useApply(id: string) {
  const queryClient = useQueryClient()
  return (updated: TrainingSession) => {
    queryClient.setQueryData(['training-session', id], updated)
    void queryClient.invalidateQueries({ queryKey: ['training-sessions'] })
    void queryClient.invalidateQueries({ queryKey: ['history', 'training_sessions', id] })
  }
}

function RescheduleForm({ session, onDone }: { session: TrainingSession; onDone: () => void }) {
  const apply = useApply(session.id)
  const [startsOn, setStartsOn] = useState(session.startsOn)
  const [endsOn, setEndsOn] = useState(session.endsOn)
  const mutation = useMutation({
    mutationFn: () => rescheduleTrainingSession(session.id, startsOn, endsOn),
    onSuccess: (updated) => {
      apply(updated)
      onDone()
    },
  })
  const error = errorText(mutation.error)
  return (
    <form onSubmit={(e: FormEvent) => { e.preventDefault(); mutation.mutate() }} noValidate className="mt-4 space-y-3 rounded-md border border-brand-100 p-4" aria-label="Reporter la session">
      <div className="grid gap-4 sm:grid-cols-2">
        <label className="block text-sm font-medium text-brand-900">
          Nouvelle date de début
          <input type="date" className={inputClass} value={startsOn} onChange={(e) => { setStartsOn(e.target.value); mutation.reset() }} />
        </label>
        <label className="block text-sm font-medium text-brand-900">
          Nouvelle date de fin
          <input type="date" className={inputClass} min={startsOn} value={endsOn} onChange={(e) => { setEndsOn(e.target.value); mutation.reset() }} />
        </label>
      </div>
      {error && <p role="alert" className="text-sm font-medium text-red-700">{error}</p>}
      <div className="flex flex-wrap gap-3">
        <button type="submit" disabled={mutation.isPending} className={primary}>Enregistrer les nouvelles dates</button>
        <button type="button" onClick={onDone} className={secondary}>Annuler</button>
      </div>
    </form>
  )
}

function CancelForm({ session, onDone }: { session: TrainingSession; onDone: () => void }) {
  const apply = useApply(session.id)
  const [reason, setReason] = useState('')
  const mutation = useMutation({
    mutationFn: () => cancelTrainingSession(session.id, reason),
    onSuccess: (updated) => {
      apply(updated)
      onDone()
    },
  })
  const error = errorText(mutation.error)
  return (
    <form onSubmit={(e: FormEvent) => { e.preventDefault(); mutation.mutate() }} noValidate className="mt-4 space-y-3 rounded-md border border-brand-100 p-4" aria-label="Annuler la session">
      <label className="block text-sm font-medium text-brand-900">
        Motif de l'annulation
        <textarea className={inputClass} rows={2} maxLength={2000} value={reason} onChange={(e) => { setReason(e.target.value); mutation.reset() }} />
      </label>
      {error && <p role="alert" className="text-sm font-medium text-red-700">{error}</p>}
      <div className="flex flex-wrap gap-3">
        <button type="submit" disabled={mutation.isPending} className={primary}>Annuler la session</button>
        <button type="button" onClick={onDone} className={secondary}>Revenir</button>
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

function SessionDetails({ id, viewer }: { id: string; viewer: Viewer }) {
  const location = useLocation()
  const apply = useApply(id)
  const [mode, setMode] = useState<'view' | 'reschedule' | 'cancel'>('view')
  const session = useQuery({ queryKey: ['training-session', id], queryFn: () => fetchTrainingSession(id) })
  const restore = useMutation({ mutationFn: () => restoreTrainingSession(id), onSuccess: apply })

  if (session.isPending) return <p className="text-brand-900">Chargement…</p>
  if (session.isError) return <p role="alert" className="font-medium text-red-700">{errorText(session.error)}</p>

  const s = session.data
  const admin = isAdmin(viewer.roles)
  const planner = canPlanSession(viewer.roles)
  const canReschedule = planner && (s.status === 'planned' || (s.status === 'finished' && admin))
  const created = (location.state as { created?: boolean } | null)?.created
  return (
    <>
      <p className="mb-2 text-sm">
        <Link to="/sessions" className="text-brand-700 underline">Sessions</Link>
      </p>
      {created && mode === 'view' && (
        <p role="status" className="mb-4 rounded-md bg-brand-50 px-3 py-2 font-medium text-brand-900">Session planifiée.</p>
      )}
      <div className="flex flex-wrap items-center gap-3">
        <h1 className="text-lg font-semibold text-brand-900">
          {s.trainingTitle}
          {s.label && <span className="ml-2 font-normal text-brand-700">— {s.label}</span>}
        </h1>
        <SessionStatusBadge status={s.status} />
      </div>
      <dl className="mt-4 grid gap-3 sm:grid-cols-2">
        <Field label="Dates">{formatPeriod(s.startsOn, s.endsOn)}</Field>
        <Field label="Formation">
          <Link to={`/formations/${s.trainingId}`} className="text-brand-700 underline">{s.trainingTitle}</Link>
        </Field>
        <Field label="En réponse à">
          {s.requestId ? (
            <Link to={`/demandes/${s.requestId}`} className="text-brand-700 underline">la demande de {s.requestService}</Link>
          ) : (
            'aucune demande'
          )}
        </Field>
        <Field label="Planifiée par">{s.plannedByName}</Field>
        {s.status === 'cancelled' && <Field label="Motif de l'annulation">{s.cancelReason}</Field>}
      </dl>
      {mode === 'view' && planner && (
        <div className="mt-4 flex flex-wrap gap-3">
          {canReschedule && <button type="button" className={primary} onClick={() => setMode('reschedule')}>Reporter</button>}
          {s.status !== 'cancelled' && <button type="button" className={secondary} onClick={() => setMode('cancel')}>Annuler la session</button>}
          {s.status === 'cancelled' && admin && (
            <button type="button" className={secondary} disabled={restore.isPending} onClick={() => restore.mutate()}>
              Remettre en « planifiée »
            </button>
          )}
        </div>
      )}
      {restore.error && <p role="alert" className="mt-2 text-sm font-medium text-red-700">{errorText(restore.error)}</p>}
      {mode === 'reschedule' && <RescheduleForm session={s} onDone={() => setMode('view')} />}
      {mode === 'cancel' && <CancelForm session={s} onDone={() => setMode('view')} />}
      <HistoryPanel subjectType="training_sessions" subjectId={s.id} emptyText="Aucune entrée au journal." />
    </>
  )
}

export function SessionPage() {
  const { id = '' } = useParams()
  return (
    <AppShell>
      {(viewer) =>
        canSeeCatalogue(viewer.roles) ? (
          <div className="max-w-3xl">
            <SessionDetails id={id} viewer={viewer} />
          </div>
        ) : (
          <AccessDenied />
        )
      }
    </AppShell>
  )
}
