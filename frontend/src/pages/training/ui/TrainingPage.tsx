import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { useState, type FormEvent } from 'react'
import { Link, useLocation, useParams } from 'react-router-dom'
import { HistoryPanel } from '../../../entities/history'
import {
  TrainingFields,
  fetchDomains,
  fetchTraining,
  updateTraining,
  type Training,
  type TrainingInput,
} from '../../../entities/training'
import { canSeeCatalogue, isAdmin, type Viewer } from '../../../entities/viewer'
import { ApiError } from '../../../shared/api'
import { AccessDenied } from '../../../shared/ui'
import { AppShell } from '../../../widgets/app-shell'

/** La modification par l'administrateur (affinage de l'Epic 2, Q4). */
function EditForm({ training, onDone }: { training: Training; onDone: () => void }) {
  const queryClient = useQueryClient()
  const [value, setValue] = useState<TrainingInput>({
    title: training.title,
    description: training.description ?? '',
    subdomainId: training.subdomainId,
  })
  const domains = useQuery({ queryKey: ['domains'], queryFn: fetchDomains })
  const mutation = useMutation({
    mutationFn: () => updateTraining(training.id, value),
    onSuccess: (updated) => {
      queryClient.setQueryData(['training', training.id], updated)
      void queryClient.invalidateQueries({ queryKey: ['trainings'] })
      void queryClient.invalidateQueries({ queryKey: ['history', 'trainings', training.id] })
      onDone()
    },
  })

  function submit(event: FormEvent) {
    event.preventDefault()
    mutation.mutate()
  }

  const error =
    mutation.error instanceof ApiError ? mutation.error.message : mutation.error ? 'Le serveur ne répond pas.' : null

  return (
    <form onSubmit={submit} noValidate className="space-y-4 rounded-md border border-brand-100 p-4">
      <TrainingFields
        value={value}
        domains={domains.data ?? []}
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
        <button
          type="submit"
          disabled={!value.title.trim() || !value.subdomainId || mutation.isPending}
          className="rounded-md bg-brand-700 px-4 py-2 font-medium text-white hover:bg-brand-600 disabled:opacity-60"
        >
          {mutation.isPending ? 'Enregistrement…' : 'Enregistrer les modifications'}
        </button>
        <button type="button" onClick={onDone} className="rounded-md border border-brand-100 px-4 py-2 font-medium text-brand-900">
          Annuler
        </button>
      </div>
    </form>
  )
}

function TrainingDetails({ id, viewer }: { id: string; viewer: Viewer }) {
  const location = useLocation()
  const [editing, setEditing] = useState(false)
  const training = useQuery({ queryKey: ['training', id], queryFn: () => fetchTraining(id) })

  if (training.isPending) return <p className="text-brand-900">Chargement…</p>
  if (training.isError) {
    return (
      <p role="alert" className="font-medium text-red-700">
        {training.error instanceof ApiError ? training.error.message : 'Le serveur ne répond pas.'}
      </p>
    )
  }

  const t = training.data
  const created = (location.state as { created?: boolean } | null)?.created
  return (
    <>
      <p className="mb-2 text-sm">
        <Link to="/formations" className="text-brand-700 underline">
          Formations
        </Link>
      </p>
      {created && !editing && (
        <p role="status" className="mb-4 rounded-md bg-brand-50 px-3 py-2 font-medium text-brand-900">
          Formation enregistrée.
        </p>
      )}
      <h1 className="text-lg font-semibold text-brand-900">{t.title}</h1>
      <p className="mb-4 text-sm text-brand-700">
        {t.domainName} › {t.subdomainName}
      </p>
      {editing ? (
        <EditForm training={t} onDone={() => setEditing(false)} />
      ) : (
        <>
          <p className="whitespace-pre-line text-brand-900">{t.description ?? 'Pas de description.'}</p>
          {isAdmin(viewer.roles) && (
            <button
              type="button"
              onClick={() => setEditing(true)}
              className="mt-4 rounded-md border border-brand-100 px-4 py-2 text-sm font-medium text-brand-900 hover:bg-brand-50"
            >
              Modifier
            </button>
          )}
        </>
      )}
      <HistoryPanel subjectType="trainings" subjectId={t.id} emptyText="Aucune entrée au journal." />
    </>
  )
}

export function TrainingPage() {
  const { id = '' } = useParams()
  return (
    <AppShell>
      {(viewer) =>
        canSeeCatalogue(viewer.roles) ? (
          <div className="max-w-3xl">
            <TrainingDetails id={id} viewer={viewer} />
          </div>
        ) : (
          <AccessDenied />
        )
      }
    </AppShell>
  )
}
