import { API_BASE_URL } from '../config'

/** Une erreur renvoyée par l'API. `message` est le texte du serveur, en
 *  français, à afficher tel quel ; sinon un message générique. */
export class ApiError extends Error {
  readonly status: number

  constructor(status: number, message?: string) {
    super(message ?? `La requête a échoué (statut ${status}).`)
    this.status = status
  }
}

async function readError(response: Response): Promise<ApiError> {
  try {
    const body = (await response.json()) as { detail?: unknown }
    if (typeof body.detail === 'string') {
      return new ApiError(response.status, body.detail)
    }
  } catch {
    // Pas de corps JSON : on garde le message générique.
  }
  return new ApiError(response.status)
}

export async function apiGet<T>(path: string): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${path}`, { credentials: 'same-origin' })
  if (!response.ok) {
    throw await readError(response)
  }
  return (await response.json()) as T
}

export async function apiPost(path: string, body: unknown): Promise<void> {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    method: 'POST',
    credentials: 'same-origin',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  })
  if (!response.ok) {
    throw await readError(response)
  }
}
