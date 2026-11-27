/** Les genres de fiches qui ont un historique (bll_history._READERS). */
export type SubjectType = 'users' | 'trainings' | 'domains' | 'subdomains' | 'training_requests' | 'training_sessions'

export type HistoryEntry = {
  occurredAt: string
  actorUserId: string | null
  actorLabel: string
  /** « Prénom Nom (badge) », donné par le serveur quand l'auteur est un utilisateur. */
  actorName: string | null
  tableName: string
  action: 'create' | 'update' | 'delete'
  before: Record<string, unknown> | null
  after: Record<string, unknown> | null
}

/** Qui a fait la modification : son nom, sinon le libellé du journal. */
export function authorOf(entry: HistoryEntry): string {
  return entry.actorName ?? entry.actorLabel
}
