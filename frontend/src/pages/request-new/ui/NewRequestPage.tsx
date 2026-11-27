import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { useState, type FormEvent } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { fetchTrainings, trainingOptions } from '../../../entities/training'
import { RequestFields, createTrainingRequest, localToday, type TrainingRequestInput } from '../../../entities/training-request'
import { canRecordTraining } from '../../../entities/viewer'
import { ApiError } from '../../../shared/api'
import { AccessDenied } from '../../../shared/ui'
import { AppShell } from '../../../widgets/app-shell'

function NewRequestForm() {
  const navigate = useNavigate()
  const queryClient = useQueryClient()
  const trainings = useQuery({ queryKey: ['trainings'], queryFn: fetchTrainings })
  const [value, setValue] = useState<TrainingRequestInput>({
    requestingService: '',
    isExternal: false,
    receivedOn: localToday(),
    trainingId: '',
    expectedParticipants: '',
    desiredPeriod: '',
    comment: '',
  })
  const mutation = useMutation({
    mutationFn: () => createTrainingRequest(value),
    onSuccess: (request) => {
      void queryClient.invalidateQueries({ queryKey: ['training-requests'] })
      navigate(`/demandes/${request.id}`, { state: { created: true } })
    },
  })

  function submit(event: FormEvent) {
    event.preventDefault()
    mutation.mutate()
  }

  const error = mutation.error instanceof ApiError ? mutation.error.message : mutation.error ? 'Le serveur ne répond pas.' : null
  const complete = Boolean(value.requestingService.trim() && value.trainingId && value.expectedParticipants)

  return (
    <form onSubmit={submit} noValidate className="space-y-4">
      <RequestFields
        value={value}
        trainings={trainingOptions(trainings.data ?? [])}
        canCreateTraining
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
          {mutation.isPending ? 'Enregistrement…' : 'Enregistrer la demande'}
        </button>
        <Link to="/demandes" className="rounded-md border border-brand-100 px-4 py-2 font-medium text-brand-900">
          Annuler
        </Link>
      </div>
    </form>
  )
}

export function NewRequestPage() {
  return (
    <AppShell>
      {(viewer) =>
        canRecordTraining(viewer.roles) ? (
          <div className="max-w-xl">
            <h1 className="mb-6 text-lg font-semibold text-brand-900">Nouvelle demande de formation</h1>
            <NewRequestForm />
          </div>
        ) : (
          <AccessDenied />
        )
      }
    </AppShell>
  )
}
