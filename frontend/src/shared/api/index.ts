import { API_BASE_URL } from '../config'

export class ApiError extends Error {
  readonly status: number

  constructor(status: number) {
    super(`La requête a échoué (statut ${status}).`)
    this.status = status
  }
}

export async function apiGet<T>(path: string): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${path}`, { credentials: 'same-origin' })
  if (!response.ok) {
    throw new ApiError(response.status)
  }
  return (await response.json()) as T
}
