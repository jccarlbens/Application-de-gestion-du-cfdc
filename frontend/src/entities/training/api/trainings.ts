import { apiGet, apiPostJson, apiPut } from '../../../shared/api'
import type {
  Domain,
  Module,
  ModuleInput,
  MyTraining,
  Subdomain,
  Trainer,
  Training,
  TrainingInput,
} from '../model/training'

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

// --- Modules et formateurs (US-011) ------------------------------------------------

type TrainerDto = {
  id: string
  first_name: string
  last_name: string
  badge: string
  is_active: boolean
  is_trainer: boolean
}
type ModuleDto = {
  id: string
  training_id: string
  title: string
  description: string | null
  trainer: TrainerDto | null
}

const toTrainer = (dto: TrainerDto): Trainer => ({
  id: dto.id,
  firstName: dto.first_name,
  lastName: dto.last_name,
  badge: dto.badge,
  isActive: dto.is_active,
  isTrainer: dto.is_trainer,
})

const toModule = (dto: ModuleDto): Module => ({
  id: dto.id,
  trainingId: dto.training_id,
  title: dto.title,
  description: dto.description,
  trainer: dto.trainer ? toTrainer(dto.trainer) : null,
})

function toModuleBody(input: ModuleInput) {
  return { title: input.title, description: input.description.trim() || null, trainer_id: input.trainerId || null }
}

export async function fetchTrainers(): Promise<Trainer[]> {
  return (await apiGet<TrainerDto[]>('/trainers')).map(toTrainer)
}

export async function fetchModules(trainingId: string): Promise<Module[]> {
  return (await apiGet<ModuleDto[]>(`/trainings/${encodeURIComponent(trainingId)}/modules`)).map(toModule)
}

export async function addModule(trainingId: string, input: ModuleInput): Promise<Module> {
  return toModule(await apiPostJson<ModuleDto>(`/trainings/${trainingId}/modules`, toModuleBody(input)))
}

export async function assignTrainer(moduleId: string, trainerId: string): Promise<Module> {
  return toModule(await apiPostJson<ModuleDto>(`/modules/${moduleId}/trainer`, { trainer_id: trainerId }))
}

export async function updateModule(moduleId: string, input: ModuleInput): Promise<Module> {
  return toModule(await apiPut<ModuleDto>(`/modules/${moduleId}`, toModuleBody(input)))
}

// --- « Mes modules » du formateur (US-013) -------------------------------------------

type MyTrainingDto = {
  id: string
  title: string
  description: string | null
  domain_name: string
  subdomain_name: string
  modules: {
    id: string
    title: string
    description: string | null
    documents: { id: string; file_name: string; size_bytes: number; uploaded_at: string }[]
  }[]
}

export async function fetchMyModules(): Promise<MyTraining[]> {
  return (await apiGet<MyTrainingDto[]>('/me/modules')).map((t) => ({
    id: t.id,
    title: t.title,
    description: t.description,
    domainName: t.domain_name,
    subdomainName: t.subdomain_name,
    modules: t.modules.map((m) => ({
      id: m.id,
      title: m.title,
      description: m.description,
      documents: m.documents.map((d) => ({ id: d.id, fileName: d.file_name, sizeBytes: d.size_bytes, uploadedAt: d.uploaded_at })),
    })),
  }))
}
