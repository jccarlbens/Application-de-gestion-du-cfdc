import { SESSION_STATUS_LABELS, type SessionStatus } from '../model/trainingSession'

const COLORS: Record<SessionStatus, string> = {
  planned: 'bg-brand-100 text-brand-900',
  finished: 'bg-green-100 text-green-900',
  cancelled: 'bg-gray-200 text-gray-800',
}

export function SessionStatusBadge({ status }: { status: SessionStatus }) {
  return <span className={`rounded-md px-2 py-0.5 text-xs font-medium ${COLORS[status]}`}>{SESSION_STATUS_LABELS[status]}</span>
}
