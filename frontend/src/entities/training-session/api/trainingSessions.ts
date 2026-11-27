import { apiGet, apiPostAction, apiPostJson, apiPut } from '../../../shared/api'
import type { SessionStatus, TrainingSession } from '../model/trainingSession'

type Dto = {
  id: string
  training_id: string
  training_title: string
  request_id: string | null
  request_service: string | null
  label: string | null
  starts_on: string
  ends_on: string
  status: SessionStatus
  cancel_reason: string | null
  planned_by_name: string
}

const toSession = (d: Dto): TrainingSession => ({
  id: d.id,
  trainingId: d.training_id,
  trainingTitle: d.training_title,
  requestId: d.request_id,
  requestService: d.request_service,
  label: d.label,
  startsOn: d.starts_on,
  endsOn: d.ends_on,
  status: d.status,
  cancelReason: d.cancel_reason,
  plannedByName: d.planned_by_name,
})

export type SessionScope = { trainingId?: string; requestId?: string }

export async function fetchTrainingSessions(scope: SessionScope = {}): Promise<TrainingSession[]> {
  const path = scope.trainingId
    ? `/trainings/${scope.trainingId}/sessions`
    : scope.requestId
      ? `/training-requests/${scope.requestId}/sessions`
      : '/training-sessions'
  return (await apiGet<Dto[]>(path)).map(toSession)
}

export async function fetchTrainingSession(id: string): Promise<TrainingSession> {
  return toSession(await apiGet<Dto>(`/training-sessions/${encodeURIComponent(id)}`))
}

export type SessionPlan = { trainingId: string; requestId: string; label: string; startsOn: string; endsOn: string }

export async function planTrainingSession(plan: SessionPlan): Promise<TrainingSession> {
  return toSession(
    await apiPostJson<Dto>('/training-sessions', {
      training_id: plan.requestId ? null : plan.trainingId || null,
      request_id: plan.requestId || null,
      label: plan.label.trim() || null,
      starts_on: plan.startsOn || null,
      ends_on: plan.endsOn || null,
    }),
  )
}

export async function rescheduleTrainingSession(id: string, startsOn: string, endsOn: string): Promise<TrainingSession> {
  return toSession(await apiPut<Dto>(`/training-sessions/${id}/dates`, { starts_on: startsOn || null, ends_on: endsOn || null }))
}

export async function cancelTrainingSession(id: string, reason: string): Promise<TrainingSession> {
  return toSession(await apiPostJson<Dto>(`/training-sessions/${id}/cancel`, { reason: reason.trim() || null }))
}

export async function restoreTrainingSession(id: string): Promise<TrainingSession> {
  return toSession(await apiPostAction<Dto>(`/training-sessions/${id}/restore`))
}
