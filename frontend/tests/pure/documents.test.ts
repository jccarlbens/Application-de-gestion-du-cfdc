import { formatSize } from '../../src/entities/document'
import { describeEntry, type HistoryEntry } from '../../src/entities/history'

describe('formatSize', () => {
  it.each([
    [300, '1 Ko'],
    [850 * 1024, '850 Ko'],
    [2.4 * 1024 * 1024, '2,4 Mo'],
    [25 * 1024 * 1024, '25 Mo'],
  ])('%#', (bytes, label) => {
    expect(formatSize(bytes)).toBe(label)
  })
})

function entry(partial: Partial<HistoryEntry>): HistoryEntry {
  return {
    occurredAt: '2026-11-20T15:21:00Z', actorUserId: 'u-1', actorLabel: 'Utilisateur connecté',
    actorName: 'Ada Admin (Z01-01)', tableName: 'course_documents', action: 'create', before: null, after: null,
    ...partial,
  }
}

describe('describeEntry pour les documents', () => {
  it('nomme le fichier et le module quand il est connu', () => {
    expect(describeEntry(entry({ after: { file_name: 'Cours.pdf', module_id: 'm-1' } }), { 'm-1': 'Vitesses' })).toEqual({
      text: 'Document déposé : « Cours.pdf » (module « Vitesses »)',
      needsDetails: false,
    })
  })

  it('raconte le remplacement', () => {
    expect(
      describeEntry(
        entry({
          action: 'update',
          before: { file_name: 'Cours.pdf', module_id: 'm-1', replaced_by_id: null },
          after: { file_name: 'Cours.pdf', module_id: 'm-1', replaced_by_id: 'd-2' },
        }),
      ),
    ).toEqual({ text: 'Document remplacé par une nouvelle version : « Cours.pdf »', needsDetails: false })
  })
})
