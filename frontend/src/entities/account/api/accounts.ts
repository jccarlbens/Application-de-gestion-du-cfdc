import { apiGet, apiPostAction, apiPostJson, apiPut } from '../../../shared/api'
import { isRole } from '../../viewer/@x/account'
import type { Account, NewAccount } from '../model/account'

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
