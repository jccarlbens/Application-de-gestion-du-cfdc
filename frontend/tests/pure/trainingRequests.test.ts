import { describeEntry, type HistoryEntry } from '../../src/entities/history'
import { formatDate, localToday } from '../../src/entities/training-request'

describe('les dates des demandes', () => {
  it("donne « aujourd'hui » dans le calendrier de l'AAN, pas en UTC", () => {
    // 2 h UTC le 25 = 21 h le 24 à Port-au-Prince.
    expect(localToday(new Date('2026-11-25T02:00:00Z'))).toBe('2026-11-24')
  })

  it('écrit une date du calendrier sans la décaler', () => {
    expect(formatDate('2026-11-20')).toBe('20/11/2026')
  })
})

function entry(partial: Partial<HistoryEntry>): HistoryEntry {
  return {
    occurredAt: '2026-11-24T15:00:00Z', actorUserId: 'u', actorLabel: 'Utilisateur connecté', actorName: 'Rose Pierre (E05-55)',
    tableName: 'training_requests', action: 'update', before: null, after: null, ...partial,
  }
}

describe('describeEntry pour les demandes de formation', () => {
  it.each([
    [entry({ action: 'create', after: { requesting_service: 'Service de sûreté' } }), 'Demande enregistrée : Service de sûreté', false],
    [entry({ before: { status: 'pending' }, after: { status: 'approved', decided_by: 'u' } }), 'Demande validée', false],
    [
      entry({ before: { status: 'pending', decision_reason: null }, after: { status: 'refused', decision_reason: 'Pas de formateur' } }),
      'Demande refusée : Pas de formateur',
      false,
    ],
    [
      entry({ before: { status: 'approved' }, after: { status: 'refused', decision_reason: 'En double' } }),
      'Demande refusée (décision corrigée) : En double',
      false,
    ],
    [
      entry({ before: { expected_participants: 12, comment: null }, after: { expected_participants: 40, comment: 'x' } }),
      'Demande ajustée : nombre de participants prévu, commentaire',
      true,
    ],
  ])('%#', (input, text, needsDetails) => {
    expect(describeEntry(input)).toEqual({ text, needsDetails })
  })
})
