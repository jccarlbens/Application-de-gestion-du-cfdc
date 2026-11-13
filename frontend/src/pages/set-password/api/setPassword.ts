import { apiPost } from '../../../shared/api'

export function setPasswordWithLink(token: string, password: string): Promise<void> {
  return apiPost('/password/setup', { token, password })
}
