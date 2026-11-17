import { apiPostJson } from '../../../shared/api'

export function login(badge: string, password: string): Promise<unknown> {
  return apiPostJson('/auth/login', { badge, password })
}
