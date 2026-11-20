import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { useState, type FormEvent } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { TrainingFields, createTraining, fetchDomains, type TrainingInput } from '../../../entities/training'
import { canRecordTraining } from '../../../entities/viewer'
import { ApiError } from '../../../shared/api'
import { AccessDenied } from '../../../shared/ui'
import { AppShell } from '../../../widgets/app-shell'

const EMPTY: TrainingInput = { title: '', description: '', subdomainId: '' }

function NewTrainingForm() {
  const navigate = useNavigate()
  const queryClient = useQueryClient()
  const [value, setValue] = useState(EMPTY)
  const domains = useQuery({ queryKey: ['domains'], queryFn: fetchDomains })
  const mutation = useMutation({
    mutationFn: () => createTraining(value),
    onSuccess: (training) => {
      void queryClient.invalidateQueries({ queryKey: ['trainings'] })
      navigate(`/formations/${training.id}`, { state: { created: true } })
    },
  })

  function submit(event: FormEvent) {
    event.preventDefault()
    mutation.mutate()
  }

  const error =
    mutation.error instanceof ApiError ? mutation.error.message : mutation.error ? 'Le serveur ne répond pas.' : null
  const complete = Boolean(value.title.trim() && value.subdomainId)

  return (
    <form onSubmit={submit} noValidate className="space-y-4">
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
          disabled={!complete || mutation.isPending}
          className="rounded-md bg-brand-700 px-4 py-2 font-medium text-white hover:bg-brand-600 disabled:opacity-60"
        >
          {mutation.isPending ? 'Enregistrement…' : 'Enregistrer la formation'}
        </button>
        <Link to="/formations" className="rounded-md border border-brand-100 px-4 py-2 font-medium text-brand-900">
          Annuler
        </Link>
      </div>
    </form>
  )
}

export function NewTrainingPage() {
  return (
    <AppShell>
      {(viewer) =>
        canRecordTraining(viewer.roles) ? (
          <div className="max-w-xl">
            <h1 className="mb-6 text-lg font-semibold text-brand-900">Nouvelle formation</h1>
            <NewTrainingForm />
          </div>
        ) : (
          <AccessDenied />
        )
      }
    </AppShell>
  )
}
