import { apiGet } from '../../../shared/api'
import type { HistoryEntry, SubjectType } from '../model/history'

type HistoryEntryDto = {
  occurred_at: string
  actor_user_id: string | null
  actor_label: string
  actor_name: string | null
  table_name: string
  action: 'create' | 'update' | 'delete'
  before: Record<string, unknown> | null
  after: Record<string, unknown> | null
}

export function toHistoryEntry(dto: HistoryEntryDto): HistoryEntry {
  return {
    occurredAt: dto.occurred_at,
    actorUserId: dto.actor_user_id,
    actorLabel: dto.actor_label,
    actorName: dto.actor_name ?? null,
    tableName: dto.table_name,
    action: dto.action,
    before: dto.before,
    after: dto.after,
  }
}

export async function fetchHistory(subjectType: SubjectType, id: string): Promise<HistoryEntry[]> {
  return (await apiGet<HistoryEntryDto[]>(`/history/${subjectType}/${id}`)).map(toHistoryEntry)
}
