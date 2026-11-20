import { describeEntry, type HistoryEntry } from '../../src/entities/history'
import { trainerLabel, type Trainer } from '../../src/entities/training'

const paul: Trainer = { id: 'p', firstName: 'Paul', lastName: 'Michel', badge: 'C03-15', isActive: true, isTrainer: true }

describe('trainerLabel', () => {
  it.each([
    [null, 'Formateur à désigner'],
    [paul, 'Paul Michel (C03-15)'],
    [{ ...paul, isActive: false }, 'Paul Michel (C03-15) (compte désactivé)'],
    [{ ...paul, isTrainer: false }, "Paul Michel (C03-15) (n'est plus formateur)"],
  ])('%#', (trainer, label) => {
    expect(trainerLabel(trainer)).toBe(label)
  })
})

function entry(partial: Partial<HistoryEntry>): HistoryEntry {
  return {
    occurredAt: '2026-11-20T15:21:00Z',
    actorUserId: 'u-1',
    actorLabel: 'Utilisateur connecté',
    actorName: 'Sonia Saintil (S02-02)',
    tableName: 'modules',
    action: 'update',
    before: null,
    after: null,
    ...partial,
  }
}

const NAMES = { p: 'Paul Michel (C03-15)', r: 'Rose Pierre (E05-55)' }

describe('describeEntry pour les modules', () => {
  it.each([
    [entry({ action: 'create', after: { title: 'Vitesses', trainer_id: null } }), 'Module ajouté : « Vitesses » — formateur à désigner', false],
    [entry({ action: 'create', after: { title: 'Vitesses', trainer_id: 'p' } }), 'Module ajouté : « Vitesses » — formateur : Paul Michel (C03-15)', false],
    [
      entry({ before: { title: 'Vitesses', trainer_id: null }, after: { title: 'Vitesses', trainer_id: 'p' } }),
      'Formateur désigné pour « Vitesses » : Paul Michel (C03-15)',
      false,
    ],
    [
      entry({ before: { title: 'Vitesses', trainer_id: 'p' }, after: { title: 'Vitesses', trainer_id: 'r' } }),
      'Formateur changé pour « Vitesses » : Rose Pierre (E05-55)',
      false,
    ],
    [
      entry({ before: { title: 'Vitesses', trainer_id: 'p' }, after: { title: 'Vitesses', trainer_id: 'x' } }),
      'Formateur du module « Vitesses » modifié',
      true,
    ],
    [
      entry({ before: { title: 'Vitesse', title_key: 'vitesse' }, after: { title: 'Vitesses', title_key: 'vitesses' } }),
      'Module renommé : « Vitesse » devient « Vitesses »',
      false,
    ],
  ])('%#', (input, text, needsDetails) => {
    expect(describeEntry(input, NAMES)).toEqual({ text, needsDetails })
  })
})
