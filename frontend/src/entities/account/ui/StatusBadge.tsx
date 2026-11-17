import { STATUS_LABELS, type AccountStatus } from '../model/account'

const STYLES: Record<AccountStatus, string> = {
  active: 'bg-brand-100 text-brand-900',
  deactivated: 'bg-gray-200 text-gray-800',
  blocked: 'bg-red-100 text-red-800',
  'awaiting-password': 'bg-amber-100 text-amber-900',
}

export function StatusBadge({ status }: { status: AccountStatus }) {
  return (
    <span className={`inline-block rounded-md px-2 py-0.5 text-xs font-medium ${STYLES[status]}`}>
      {STATUS_LABELS[status]}
    </span>
  )
}
