export type RequestStatus = 'pending' | 'approved' | 'refused'

export const STATUS_LABELS: Record<RequestStatus, string> = {
  pending: 'En attente',
  approved: 'Validée',
  refused: 'Refusée',
}

/** Une demande de formation (US-014) ; à ne pas confondre avec une demande de correction. */
export type TrainingRequest = {
  id: string
  requestingService: string
  isExternal: boolean
  receivedOn: string
  trainingId: string
  trainingTitle: string
  expectedParticipants: number
  desiredPeriod: string | null
  comment: string | null
  status: RequestStatus
  decidedByName: string | null
  decidedAt: string | null
  decisionReason: string | null
  recordedByName: string
}

export type TrainingRequestInput = {
  requestingService: string
  isExternal: boolean
  receivedOn: string
  trainingId: string
  expectedParticipants: string
  desiredPeriod: string
  comment: string
}

// Les limites vérifiées par le serveur (US-014, décision 4), rappelées à l'écran.
export const SERVICE_MAX = 150
export const PERIOD_MAX = 100
export const TEXT_MAX = 2000

/** « Aujourd'hui » dans le calendrier de l'AAN (AAAA-MM-JJ), pas celui de l'appareil en UTC. */
export function localToday(now: Date = new Date()): string {
  return new Intl.DateTimeFormat('en-CA', { timeZone: 'America/Port-au-Prince' }).format(now)
}

/** Une date du calendrier, sans fuseau : « 20/11/2026 ». */
export function formatDate(isoDate: string): string {
  const [year, month, day] = isoDate.split('-')
  return `${day}/${month}/${year}`
}
