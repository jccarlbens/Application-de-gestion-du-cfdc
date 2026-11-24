import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { useState, type FormEvent } from 'react'
import { Link, useNavigate, useSearchParams } from 'react-router-dom'
import { fetchTrainings, trainingOptions } from '../../../entities/training'
import { fetchTrainingRequest } from '../../../entities/training-request'
import { LABEL_MAX, planTrainingSession } from '../../../entities/training-session'
import { canPlanSession } from '../../../entities/viewer'
import { ApiError } from '../../../shared/api'
import { AccessDenied } from '../../../shared/ui'
import { AppShell } from '../../../widgets/app-shell'

const inputClass =
  'mt-1 w-full rounded-md border border-brand-100 px-3 py-2 focus:border-brand-600 focus:outline-none focus:ring-2 focus:ring-brand-100'

/** Planifier une session, depuis une formation (`?formation=`), une demande
 *  validée (`?demande=`, la formation est alors celle de la demande) ou seule. */
function NewSessionForm() {
  const [params] = useSearchParams()
  const requestId = params.get('demande') ?? ''
  const navigate = useNavigate()
  const queryClient = useQueryClient()
  const trainings = useQuery({ queryKey: ['trainings'], queryFn: fetchTrainings, enabled: !requestId })
  const request = useQuery({ queryKey: ['training-request', requestId], queryFn: () => fetchTrainingRequest(requestId), enabled: Boolean(requestId) })
  const [trainingId, setTrainingId] = useState(params.get('formation') ?? '')
  const [label, setLabel] = useState('')
  const [startsOn, setStartsOn] = useState('')
  const [endsOn, setEndsOn] = useState('')
  const mutation = useMutation({
    mutationFn: () => planTrainingSession({ trainingId, requestId, label, startsOn, endsOn }),
    onSuccess: (session) => {
      void queryClient.invalidateQueries({ queryKey: ['training-sessions'] })
      navigate(`/sessions/${session.id}`, { state: { created: true } })
    },
  })

  function submit(event: FormEvent) {
    event.preventDefault()
    mutation.mutate()
  }

  const error = mutation.error instanceof ApiError ? mutation.error.message : mutation.error ? 'Le serveur ne répond pas.' : null
  const options = trainingOptions(trainings.data ?? [])
  const groups = [...new Set(options.map((o) => o.group))]

  return (
    <form onSubmit={submit} noValidate className="space-y-4">
      {requestId ? (
        <div className="rounded-md bg-brand-50 px-3 py-2 text-sm text-brand-900">
          En réponse à la demande de <strong>{request.data?.requestingService ?? '…'}</strong> — formation{' '}
          <strong>{request.data?.trainingTitle ?? '…'}</strong>
        </div>
      ) : (
        <label className="block text-sm font-medium text-brand-900">
          Formation
          <select className={inputClass} value={trainingId} onChange={(event) => { setTrainingId(event.target.value); mutation.reset() }}>
            <option value="">Choisir…</option>
            {groups.map((group) => (
              <optgroup key={group} label={group}>
                {options.filter((o) => o.group === group).map((o) => (
                  <option key={o.id} value={o.id}>
                    {o.title}
                  </option>
                ))}
              </optgroup>
            ))}
          </select>
        </label>
      )}
      <div className="grid gap-4 sm:grid-cols-2">
        <label className="block text-sm font-medium text-brand-900">
          Date de début
          <input type="date" className={inputClass} value={startsOn} onChange={(event) => { setStartsOn(event.target.value); mutation.reset() }} />
        </label>
        <label className="block text-sm font-medium text-brand-900">
          Date de fin
          <input type="date" className={inputClass} min={startsOn || undefined} value={endsOn} onChange={(event) => { setEndsOn(event.target.value); mutation.reset() }} />
        </label>
      </div>
      <label className="block text-sm font-medium text-brand-900">
        Libellé <span className="font-normal">(facultatif, par exemple « Groupe A »)</span>
        <input className={inputClass} maxLength={LABEL_MAX} value={label} onChange={(event) => setLabel(event.target.value)} />
      </label>
      {error && (
        <p role="alert" className="text-sm font-medium text-red-700">
          {error}
        </p>
      )}
      <div className="flex flex-wrap gap-3">
        <button
          type="submit"
          disabled={!(requestId || trainingId) || !startsOn || !endsOn || mutation.isPending}
          className="rounded-md bg-brand-700 px-4 py-2 font-medium text-white hover:bg-brand-600 disabled:opacity-60"
        >
          {mutation.isPending ? 'Enregistrement…' : 'Planifier la session'}
        </button>
        <Link to="/sessions" className="rounded-md border border-brand-100 px-4 py-2 font-medium text-brand-900">
          Annuler
        </Link>
      </div>
    </form>
  )
}

export function NewSessionPage() {
  return (
    <AppShell>
      {(viewer) =>
        canPlanSession(viewer.roles) ? (
          <div className="max-w-xl">
            <h1 className="mb-6 text-lg font-semibold text-brand-900">Planifier une session</h1>
            <NewSessionForm />
          </div>
        ) : (
          <AccessDenied />
        )
      }
    </AppShell>
  )
}
