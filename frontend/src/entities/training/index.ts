export {
  addDomain,
  addModule,
  addSubdomain,
  assignTrainer,
  createTraining,
  fetchDomains,
  fetchModules,
  fetchTraining,
  fetchTrainers,
  fetchTrainings,
  renameDomain,
  renameSubdomain,
  updateModule,
  updateTraining,
} from './api/trainings'
export { groupTrainings, type DomainGroup, type SubdomainGroup } from './lib/groupTrainings'
export {
  DESCRIPTION_MAX,
  TITLE_MAX,
  trainerLabel,
  trainerName,
  type Domain,
  type Module,
  type ModuleInput,
  type Subdomain,
  type Trainer,
  type Training,
  type TrainingInput,
} from './model/training'
export { TrainingFields } from './ui/TrainingFields'
