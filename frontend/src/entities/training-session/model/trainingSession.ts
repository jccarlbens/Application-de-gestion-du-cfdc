/** Le statut affiché : « terminée » est déduit des dates par le serveur. */
export type SessionStatus = 'planned' | 'finished' | 'cancelled'

export const SESSION_STATUS_LABELS: Record<SessionStatus, string> = {
  planned: 'Planifiée',
  finished: 'Terminée',
  cancelled: 'Annulée',
}

/** Une session de formation (US-015) ; à ne pas confondre avec une session de connexion. */
export type TrainingSession = {
  id: string
  trainingId: string
  trainingTitle: string
  requestId: string | null
  requestService: string | null
  label: string | null
  startsOn: string
  endsOn: string
  status: SessionStatus
  cancelReason: string | null
  plannedByName: string
}

export const LABEL_MAX = 100

const MONTHS = ['janvier', 'février', 'mars', 'avril', 'mai', 'juin', 'juillet', 'août', 'septembre', 'octobre', 'novembre', 'décembre']

function parts(isoDate: string): [number, string, number] {
  const [year, month, day] = isoDate.split('-').map(Number)
  return [day, MONTHS[month - 1], year]
}

/** Les dates d'une session, en clair et sans fuseau : « du 2 au 5 décembre 2026 ». */
export function formatPeriod(startsOn: string, endsOn: string): string {
  const [d1, m1, y1] = parts(startsOn)
  const [d2, m2, y2] = parts(endsOn)
  if (startsOn === endsOn) return `le ${d1} ${m1} ${y1}`
  if (m1 === m2 && y1 === y2) return `du ${d1} au ${d2} ${m2} ${y2}`
  if (y1 === y2) return `du ${d1} ${m1} au ${d2} ${m2} ${y2}`
  return `du ${d1} ${m1} ${y1} au ${d2} ${m2} ${y2}`
}
