import { describeEntry, type HistoryEntry } from '../../src/entities/history'
import { groupTrainings, type Training } from '../../src/entities/training'
import { canRecordTraining, canSeeCatalogue } from '../../src/entities/viewer'

function entry(partial: Partial<HistoryEntry>): HistoryEntry {
  return {
    occurredAt: '2026-11-20T15:21:00Z',
    actorUserId: 'u-1',
    actorLabel: 'Utilisateur connecté',
    actorName: 'Ada Admin (Z01-01)',
    tableName: 'trainings',
    action: 'update',
    before: null,
    after: null,
    ...partial,
  }
}

describe('describeEntry pour le catalogue', () => {
  it.each([
    [entry({ action: 'create', after: { title: 'Protocole' } }), 'Formation créée : « Protocole »', false],
    [
      entry({ before: { title: 'Protcole', title_key: 'protcole' }, after: { title: 'Protocole', title_key: 'protocole' } }),
      'Intitulé modifié : « Protocole »',
      false,
    ],
    [entry({ before: { description: null }, after: { description: 'Pour tous' } }), 'Description modifiée', true],
    [entry({ before: { subdomain_id: 'a' }, after: { subdomain_id: 'b' } }), 'Sous-domaine modifié', true],
    [entry({ tableName: 'domains', action: 'create', after: { name: 'Exploitation' } }), 'Domaine créé : « Exploitation »', false],
    [
      entry({ tableName: 'subdomains', before: { name: 'Balisage' }, after: { name: 'Balisage lumineux' } }),
      'Sous-domaine renommé : « Balisage » devient « Balisage lumineux »',
      false,
    ],
  ])('%#', (input, text, needsDetails) => {
    expect(describeEntry(input)).toEqual({ text, needsDetails })
  })
})

function training(title: string, domainName: string, subdomainName: string): Training {
  return {
    id: title,
    title,
    description: null,
    subdomainId: `${domainName}/${subdomainName}`,
    subdomainName,
    domainId: domainName,
    domainName,
  }
}

describe('groupTrainings', () => {
  const trainings = [
    training('Zèle', 'Accueil', 'Protocole'),
    training('Rampe 2', 'Sûreté-Sécurité', 'Conduite sur la rampe'),
    training('accueil VIP', 'Accueil', 'Protocole'),
    training('Bonjour', 'Accueil', 'Civilité'),
  ]

  it('regroupe par domaine puis sous-domaine, triés par nom sans tenir compte des majuscules', () => {
    const groups = groupTrainings(trainings)
    expect(groups.map((g) => g.domainName)).toEqual(['Accueil', 'Sûreté-Sécurité'])
    expect(groups[0].subdomains.map((s) => s.subdomainName)).toEqual(['Civilité', 'Protocole'])
    expect(groups[0].subdomains[1].trainings.map((t) => t.title)).toEqual(['accueil VIP', 'Zèle'])
  })

  it('filtre sur un domaine', () => {
    expect(groupTrainings(trainings, 'Sûreté-Sécurité').map((g) => g.domainName)).toEqual(['Sûreté-Sécurité'])
  })
})

describe('les droits du catalogue à l’écran', () => {
  it('le cache au formateur seul, pas à une personne qui a aussi un autre rôle', () => {
    expect(canSeeCatalogue(['trainer'])).toBe(false)
    expect(canSeeCatalogue(['trainer', 'secretary'])).toBe(true)
    expect(canSeeCatalogue(['direction'])).toBe(true)
  })

  it('ne laisse pas la direction enregistrer une formation', () => {
    expect(canRecordTraining(['direction'])).toBe(false)
    expect(canRecordTraining(['service_head'])).toBe(true)
  })
})
