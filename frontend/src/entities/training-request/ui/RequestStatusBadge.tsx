import { STATUS_LABELS, type RequestStatus } from '../model/trainingRequest'

const COLORS: Record<RequestStatus, string> = {
  pending: 'bg-amber-100 text-amber-900',
  approved: 'bg-green-100 text-green-900',
  refused: 'bg-gray-200 text-gray-800',
}

export function RequestStatusBadge({ status }: { status: RequestStatus }) {
  return <span className={`rounded-md px-2 py-0.5 text-xs font-medium ${COLORS[status]}`}>{STATUS_LABELS[status]}</span>
}
