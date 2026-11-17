import { apiGet, apiPost } from '../../../shared/api'
import { isRole, type Role } from '../model/roles'

type MeDto = {
  badge: string
  first_name: string
  last_name: string
  roles: string[]
}

/** La personne connectée. */
export type Viewer = {
  badge: string
  fullName: string
  roles: Role[]
}

export function toViewer(dto: MeDto): Viewer {
  return {
    badge: dto.badge,
    fullName: `${dto.first_name} ${dto.last_name}`,
    roles: dto.roles.filter(isRole),
  }
}

export async function fetchViewer(): Promise<Viewer> {
  return toViewer(await apiGet<MeDto>('/auth/me'))
}

export function logout(): Promise<void> {
  return apiPost('/auth/logout', {})
}
