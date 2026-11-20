export type Subdomain = { id: string; domainId: string; name: string }

export type Domain = { id: string; name: string; subdomains: Subdomain[] }

export type Training = {
  id: string
  title: string
  description: string | null
  subdomainId: string
  subdomainName: string
  domainId: string
  domainName: string
}

export type TrainingInput = { title: string; description: string; subdomainId: string }

// Les limites vérifiées par le serveur (US-010, décision 8), rappelées à l'écran.
export const TITLE_MAX = 200
export const DESCRIPTION_MAX = 2000

/** Un formateur, sans ses données personnelles (US-011). */
export type Trainer = {
  id: string
  firstName: string
  lastName: string
  badge: string
  isActive: boolean
  isTrainer: boolean
}

export type Module = {
  id: string
  trainingId: string
  title: string
  description: string | null
  trainer: Trainer | null
}

export type ModuleInput = { title: string; description: string; trainerId: string }

export function trainerName(trainer: Trainer): string {
  return `${trainer.firstName} ${trainer.lastName} (${trainer.badge})`
}

/** Le formateur d'un module, tel qu'on l'affiche (US-011, décision 4A). */
export function trainerLabel(trainer: Trainer | null): string {
  if (!trainer) return 'Formateur à désigner'
  if (!trainer.isActive) return `${trainerName(trainer)} (compte désactivé)`
  if (!trainer.isTrainer) return `${trainerName(trainer)} (n'est plus formateur)`
  return trainerName(trainer)
}

/** « Mes modules » (US-013) : ce que voit le formateur, sans « déposé par ». */
export type MyDocument = { id: string; fileName: string; sizeBytes: number; uploadedAt: string }
export type MyModule = { id: string; title: string; description: string | null; documents: MyDocument[] }
export type MyTraining = {
  id: string
  title: string
  description: string | null
  domainName: string
  subdomainName: string
  modules: MyModule[]
}
