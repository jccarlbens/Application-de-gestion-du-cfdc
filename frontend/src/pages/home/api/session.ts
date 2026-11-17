import { apiGet, apiPost } from '../../../shared/api'

type MeDto = {
  badge: string
  first_name: string
  last_name: string
  roles: string[]
}

export type Me = {
  badge: string
  fullName: string
}

export function toMe(dto: MeDto): Me {
  return { badge: dto.badge, fullName: `${dto.first_name} ${dto.last_name}` }
}

export async function fetchMe(): Promise<Me> {
  return toMe(await apiGet<MeDto>('/auth/me'))
}

export function logout(): Promise<void> {
  return apiPost('/auth/logout', {})
}
