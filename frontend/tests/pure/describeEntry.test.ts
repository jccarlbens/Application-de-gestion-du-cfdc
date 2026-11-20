import { accountStatus, byLastName, toAccount } from '../../src/entities/account'
import { describeEntry, type HistoryEntry } from '../../src/entities/history'

function entry(partial: Partial<HistoryEntry>): HistoryEntry {
  return {
    occurredAt: '2026-11-17T15:21:00Z',
    actorUserId: null,
    actorLabel: 'Ligne de commande (administrateur)',
    actorName: null,
    tableName: 'users',
    action: 'update',
    before: null,
    after: null,
    ...partial,
  }
}

describe('describeEntry', () => {
  it.each([
    [entry({ action: 'create', after: { badge: 'B07-42' } }), 'Compte créé (B07-42)'],
    [entry({ tableName: 'user_roles', action: 'create', after: { role: 'trainer' } }), 'Rôle ajouté : Formateur'],
    [entry({ tableName: 'user_roles', action: 'delete', before: { role: 'secretary' } }), 'Rôle retiré : Secrétaire'],
    [entry({ before: { is_active: true }, after: { is_active: false } }), 'Compte désactivé'],
    [entry({ before: { is_active: false }, after: { is_active: true } }), 'Compte réactivé'],
    [entry({ before: { is_blocked: false }, after: { is_blocked: true } }), 'Compte bloqué'],
    [
      entry({
        before: { is_blocked: true, failures_counted_since: null },
        after: { is_blocked: false, failures_counted_since: '2026-11-17T15:00:00Z' },
      }),
      'Compte débloqué',
    ],
    [entry({ before: { password_hash: null }, after: { password_hash: '[secret modifié]' } }), 'Mot de passe modifié'],
  ])('%#', (input, text) => {
    expect(describeEntry(input)).toEqual({ text, needsDetails: false })
  })

  it('dit quels champs ont changé, avec les détails', () => {
    expect(describeEntry(entry({ before: { email: 'a@x.test', phone: null }, after: { email: 'b@x.test', phone: null } }))).toEqual({
      text: 'Informations modifiées : email',
      needsDetails: true,
    })
  })

  it("renvoie aux détails pour ce qu'elle ne sait pas raconter", () => {
    expect(describeEntry(entry({ tableName: 'sessions', action: 'create', after: {} }))).toEqual({
      text: 'Création (sessions)',
      needsDetails: true,
    })
  })
})

describe('accountStatus et le tri', () => {
  const base = toAccount({
    id: '1', badge: 'B07-42', first_name: 'Marie', last_name: 'Joseph', email: 'm@x.test', phone: null,
    roles: ['secretary'], is_active: true, is_blocked: false, has_password: true,
  })

  it('donne le statut le plus important', () => {
    expect(accountStatus(base)).toBe('active')
    expect(accountStatus({ ...base, hasPassword: false })).toBe('awaiting-password')
    expect(accountStatus({ ...base, isBlocked: true, hasPassword: false })).toBe('blocked')
    expect(accountStatus({ ...base, isActive: false, isBlocked: true })).toBe('deactivated')
  })

  it('trie par nom puis prénom, à la française', () => {
    const names = [
      { ...base, lastName: 'Étienne', firstName: 'Ana' },
      { ...base, lastName: 'Joseph', firstName: 'Marie' },
      { ...base, lastName: 'Duval', firstName: 'Zoé' },
    ].sort(byLastName)
    expect(names.map((a) => a.lastName)).toEqual(['Duval', 'Étienne', 'Joseph'])
  })
})
