import type { Training } from '../model/training'

export type SubdomainGroup = { subdomainId: string; subdomainName: string; trainings: Training[] }
export type DomainGroup = { domainId: string; domainName: string; subdomains: SubdomainGroup[] }

const byName = (a: string, b: string) => a.localeCompare(b, 'fr', { sensitivity: 'base' })

/** Les formations regroupées par domaine puis par sous-domaine, tout trié par
 *  nom (US-010, décision 6). `domainId` filtre sur un seul domaine. */
export function groupTrainings(trainings: readonly Training[], domainId?: string): DomainGroup[] {
  const domains = new Map<string, DomainGroup>()
  for (const training of trainings) {
    if (domainId && training.domainId !== domainId) continue
    let domain = domains.get(training.domainId)
    if (!domain) {
      domain = { domainId: training.domainId, domainName: training.domainName, subdomains: [] }
      domains.set(training.domainId, domain)
    }
    let sub = domain.subdomains.find((s) => s.subdomainId === training.subdomainId)
    if (!sub) {
      sub = { subdomainId: training.subdomainId, subdomainName: training.subdomainName, trainings: [] }
      domain.subdomains.push(sub)
    }
    sub.trainings.push(training)
  }
  const groups = [...domains.values()].sort((a, b) => byName(a.domainName, b.domainName))
  for (const group of groups) {
    group.subdomains.sort((a, b) => byName(a.subdomainName, b.subdomainName))
    for (const sub of group.subdomains) sub.trainings.sort((a, b) => byName(a.title, b.title))
  }
  return groups
}
