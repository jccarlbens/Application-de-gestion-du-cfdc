import type { Role } from '../../viewer/@x/account'

export type Account = {
  id: string
  badge: string
  firstName: string
  lastName: string
  email: string
  phone: string | null
  roles: Role[]
  isActive: boolean
  isBlocked: boolean
  hasPassword: boolean
}

export type AccountStatus = 'active' | 'deactivated' | 'blocked' | 'awaiting-password'

export const STATUS_LABELS: Record<AccountStatus, string> = {
  active: 'Actif',
  deactivated: 'Désactivé',
  blocked: 'Bloqué',
  'awaiting-password': 'En attente du mot de passe',
}

/** Un seul statut à afficher, du plus important au moins important. */
export function accountStatus(account: Account): AccountStatus {
  if (!account.isActive) return 'deactivated'
  if (account.isBlocked) return 'blocked'
  if (!account.hasPassword) return 'awaiting-password'
  return 'active'
}

export function byLastName(a: Account, b: Account): number {
  return `${a.lastName} ${a.firstName}`.localeCompare(`${b.lastName} ${b.firstName}`, 'fr')
}

export type NewAccount = {
  badge: string
  firstName: string
  lastName: string
  email: string
  phone: string
  roles: Role[]
}

export type HistoryEntry = {
  occurredAt: string
  actorUserId: string | null
  actorLabel: string
  tableName: string
  action: 'create' | 'update' | 'delete'
  before: Record<string, unknown> | null
  after: Record<string, unknown> | null
}
