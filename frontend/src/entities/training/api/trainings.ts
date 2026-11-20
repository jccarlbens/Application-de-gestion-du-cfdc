import { apiGet, apiPostJson, apiPut } from '../../../shared/api'
import type { Domain, Subdomain, Training, TrainingInput } from '../model/training'

type SubdomainDto = { id: string; domain_id: string; name: string }
type DomainDto = { id: string; name: string; subdomains: SubdomainDto[] }
type TrainingDto = {
  id: string
  title: string
  description: string | null
  subdomain_id: string
  subdomain_name: string
  domain_id: string
  domain_name: string
}

const toSubdomain = (dto: SubdomainDto): Subdomain => ({ id: dto.id, domainId: dto.domain_id, name: dto.name })
const toDomain = (dto: DomainDto): Domain => ({ id: dto.id, name: dto.name, subdomains: dto.subdomains.map(toSubdomain) })

function toTraining(dto: TrainingDto): Training {
  return {
    id: dto.id,
    title: dto.title,
    description: dto.description,
    subdomainId: dto.subdomain_id,
    subdomainName: dto.subdomain_name,
    domainId: dto.domain_id,
    domainName: dto.domain_name,
  }
}

function toBody(input: TrainingInput) {
  return { title: input.title, description: input.description.trim() || null, subdomain_id: input.subdomainId }
}

export async function fetchDomains(): Promise<Domain[]> {
  return (await apiGet<DomainDto[]>('/domains')).map(toDomain)
}

export async function fetchTrainings(): Promise<Training[]> {
  return (await apiGet<TrainingDto[]>('/trainings')).map(toTraining)
}

export async function fetchTraining(id: string): Promise<Training> {
  return toTraining(await apiGet<TrainingDto>(`/trainings/${encodeURIComponent(id)}`))
}

export async function createTraining(input: TrainingInput): Promise<Training> {
  return toTraining(await apiPostJson<TrainingDto>('/trainings', toBody(input)))
}

export async function updateTraining(id: string, input: TrainingInput): Promise<Training> {
  return toTraining(await apiPut<TrainingDto>(`/trainings/${id}`, toBody(input)))
}

export async function addDomain(name: string): Promise<Domain> {
  return toDomain(await apiPostJson<DomainDto>('/domains', { name }))
}

export async function renameDomain(id: string, name: string): Promise<Domain> {
  return toDomain(await apiPut<DomainDto>(`/domains/${id}`, { name }))
}

export async function addSubdomain(domainId: string, name: string): Promise<Subdomain> {
  return toSubdomain(await apiPostJson<SubdomainDto>(`/domains/${domainId}/subdomains`, { name }))
}

export async function renameSubdomain(id: string, name: string): Promise<Subdomain> {
  return toSubdomain(await apiPut<SubdomainDto>(`/subdomains/${id}`, { name }))
}
