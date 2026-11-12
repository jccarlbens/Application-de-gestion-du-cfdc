import { apiGet } from '../../../shared/api'

type HealthDto = {
  status: 'ok'
  database: 'reachable' | 'unreachable'
}

export type Health = {
  isDatabaseReachable: boolean
}

export function toHealth(dto: HealthDto): Health {
  return { isDatabaseReachable: dto.database === 'reachable' }
}

export async function fetchHealth(): Promise<Health> {
  return toHealth(await apiGet<HealthDto>('/health'))
}
