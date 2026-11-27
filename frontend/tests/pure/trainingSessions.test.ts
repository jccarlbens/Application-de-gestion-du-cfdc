import { describeEntry, type HistoryEntry } from '../../src/entities/history'
import { formatPeriod } from '../../src/entities/training-session'

describe('formatPeriod', () => {
  it.each([
    ['2026-12-02', '2026-12-02', 'le 2 décembre 2026'],
    ['2026-12-02', '2026-12-05', 'du 2 au 5 décembre 2026'],
    ['2026-11-28', '2026-12-02', 'du 28 novembre au 2 décembre 2026'],
    ['2026-12-28', '2027-01-08', 'du 28 décembre 2026 au 8 janvier 2027'],
  ])('%s → %s', (start, end, text) => {
    expect(formatPeriod(start, end)).toBe(text)
  })
})

function entry(partial: Partial<HistoryEntry>): HistoryEntry {
  return {
    occurredAt: '2026-11-24T15:00:00Z', actorUserId: 'u', actorLabel: 'Utilisateur connecté', actorName: 'Rose Pierre (E05-55)',
    tableName: 'training_sessions', action: 'update', before: null, after: null, ...partial,
  }
}

describe('describeEntry pour les sessions', () => {
  it.each([
    [entry({ action: 'create', after: { starts_on: '2026-12-02', ends_on: '2026-12-05' } }), 'Session planifiée du 02/12/2026 au 05/12/2026'],
    [
      entry({ before: { starts_on: '2026-12-02', ends_on: '2026-12-05' }, after: { starts_on: '2026-12-09', ends_on: '2026-12-09' } }),
      'Session reportée : le 09/12/2026',
    ],
    [entry({ before: { status: 'planned', cancel_reason: null }, after: { status: 'cancelled', cancel_reason: 'Formateur absent' } }), 'Session annulée : Formateur absent'],
    [entry({ before: { status: 'cancelled' }, after: { status: 'planned' } }), 'Session remise en « planifiée » (annulation corrigée)'],
  ])('%#', (input, text) => {
    expect(describeEntry(input)).toEqual({ text, needsDetails: false })
  })
})
