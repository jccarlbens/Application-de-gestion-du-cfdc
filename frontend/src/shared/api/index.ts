import { API_BASE_URL } from '../config'

/** Une erreur renvoyée par l'API. `message` est le texte du serveur, en
 *  français, à afficher tel quel ; sinon un message générique. */
export class ApiError extends Error {
  readonly status: number

  constructor(status: number, message?: string) {
    super(message ?? genericMessage(status))
    this.status = status
  }
}

// Sans explication du serveur. 502, 503 et 504 viennent du relais ou de
// l'hébergeur, pas de notre code : sur le serveur de test, le backend se
// réveille ou redémarre (vu sur US-002, le 2026-11-16).
export function genericMessage(status: number): string {
  if (status === 502 || status === 503 || status === 504) {
    return 'Le serveur est momentanément indisponible. Réessayez dans une minute.'
  }
  return `La requête a échoué (statut ${status}).`
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

export async function apiPostJson<T>(path: string, body: unknown): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    method: 'POST',
    credentials: 'same-origin',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  })
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

async function send<T>(method: string, path: string, body?: unknown): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    method,
    credentials: 'same-origin',
    headers: body === undefined ? undefined : { 'Content-Type': 'application/json' },
    body: body === undefined ? undefined : JSON.stringify(body),
  })
  if (!response.ok) {
    throw await readError(response)
  }
  return (await response.json()) as T
}

export function apiPut<T>(path: string, body: unknown): Promise<T> {
  return send<T>('PUT', path, body)
}

/** Un POST sans corps qui renvoie du JSON (désactiver, réactiver, débloquer…). */
export function apiPostAction<T>(path: string): Promise<T> {
  return send<T>('POST', path)
}

