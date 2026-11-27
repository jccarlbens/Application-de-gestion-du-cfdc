import { apiGet, apiPostJson, apiPut } from '../../../shared/api'
import type { RequestStatus, TrainingRequest, TrainingRequestInput } from '../model/trainingRequest'

type Dto = {
  id: string
  requesting_service: string
  is_external: boolean
  received_on: string
  training_id: string
  training_title: string
  expected_participants: number
  desired_period: string | null
  comment: string | null
  status: RequestStatus
  decided_by_name: string | null
  decided_at: string | null
  decision_reason: string | null
  recorded_by_name: string
}

const toRequest = (d: Dto): TrainingRequest => ({
  id: d.id,
  requestingService: d.requesting_service,
  isExternal: d.is_external,
  receivedOn: d.received_on,
  trainingId: d.training_id,
  trainingTitle: d.training_title,
  expectedParticipants: d.expected_participants,
  desiredPeriod: d.desired_period,
  comment: d.comment,
  status: d.status,
  decidedByName: d.decided_by_name,
  decidedAt: d.decided_at,
  decisionReason: d.decision_reason,
  recordedByName: d.recorded_by_name,
})

function toBody(input: TrainingRequestInput) {
  const participants = Number.parseInt(input.expectedParticipants, 10)
  return {
    requesting_service: input.requestingService,
    is_external: input.isExternal,
    received_on: input.receivedOn || null,
    training_id: input.trainingId || null,
    expected_participants: Number.isNaN(participants) ? null : participants,
    desired_period: input.desiredPeriod.trim() || null,
    comment: input.comment.trim() || null,
  }
}

export async function fetchTrainingRequests(status: RequestStatus | ''): Promise<TrainingRequest[]> {
  const query = status ? `?status=${status}` : ''
  return (await apiGet<Dto[]>(`/training-requests${query}`)).map(toRequest)
}

export async function fetchTrainingRequest(id: string): Promise<TrainingRequest> {
  return toRequest(await apiGet<Dto>(`/training-requests/${encodeURIComponent(id)}`))
}

export async function createTrainingRequest(input: TrainingRequestInput): Promise<TrainingRequest> {
  return toRequest(await apiPostJson<Dto>('/training-requests', toBody(input)))
}

export async function adjustTrainingRequest(id: string, input: TrainingRequestInput): Promise<TrainingRequest> {
  return toRequest(await apiPut<Dto>(`/training-requests/${id}`, toBody(input)))
}

export async function decideTrainingRequest(
  id: string,
  status: Exclude<RequestStatus, 'pending'>,
  reason: string,
): Promise<TrainingRequest> {
  return toRequest(await apiPostJson<Dto>(`/training-requests/${id}/decision`, { status, reason: reason.trim() || null }))
}
