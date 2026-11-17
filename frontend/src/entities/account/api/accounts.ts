import { apiGet, apiPostAction, apiPostJson, apiPut } from '../../../shared/api'
import { isRole } from '../../viewer/@x/account'
import type { Account, HistoryEntry, NewAccount } from '../model/account'

type AccountDto = {
  id: string
  badge: string
  first_name: string
  last_name: string
  email: string
  phone: string | null
  roles: string[]
  is_active: boolean
  is_blocked: boolean
  has_password: boolean
}

type HistoryEntryDto = {
  occurred_at: string
  actor_user_id: string | null
  actor_label: string
  table_name: string
  action: 'create' | 'update' | 'delete'
  before: Record<string, unknown> | null
  after: Record<string, unknown> | null
}

export function toAccount(dto: AccountDto): Account {
  return {
    id: dto.id,
    badge: dto.badge,
    firstName: dto.first_name,
    lastName: dto.last_name,
    email: dto.email,
    phone: dto.phone,
    roles: dto.roles.filter(isRole),
    isActive: dto.is_active,
    isBlocked: dto.is_blocked,
    hasPassword: dto.has_password,
  }
}

function toHistoryEntry(dto: HistoryEntryDto): HistoryEntry {
  return {
    occurredAt: dto.occurred_at,
    actorUserId: dto.actor_user_id,
    actorLabel: dto.actor_label,
    tableName: dto.table_name,
    action: dto.action,
    before: dto.before,
    after: dto.after,
  }
}

export async function fetchAccounts(): Promise<Account[]> {
  return (await apiGet<AccountDto[]>('/users')).map(toAccount)
}

export async function fetchAccount(badge: string): Promise<Account> {
  return toAccount(await apiGet<AccountDto>(`/users/by-badge/${encodeURIComponent(badge)}`))
}

export async function createAccount(account: NewAccount): Promise<Account> {
  return toAccount(
    await apiPostJson<AccountDto>('/users', {
      badge: account.badge,
      first_name: account.firstName,
      last_name: account.lastName,
      email: account.email,
      phone: account.phone.trim() || null,
      roles: account.roles,
    }),
  )
}

export async function setAccountRoles(id: string, roles: string[]): Promise<Account> {
  return toAccount(await apiPut<AccountDto>(`/users/${id}/roles`, { roles }))
}

export type AccountAction = 'deactivate' | 'reactivate' | 'unblock'

export async function runAccountAction(id: string, action: AccountAction): Promise<Account> {
  return toAccount(await apiPostAction<AccountDto>(`/users/${id}/${action}`))
}

export async function fetchAccountHistory(id: string): Promise<HistoryEntry[]> {
  return (await apiGet<HistoryEntryDto[]>(`/history/users/${id}`)).map(toHistoryEntry)
}
