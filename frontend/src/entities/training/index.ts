export {
  addDomain,
  addSubdomain,
  createTraining,
  fetchDomains,
  fetchTraining,
  fetchTrainings,
  renameDomain,
  renameSubdomain,
  updateTraining,
} from './api/trainings'
export { groupTrainings, type DomainGroup, type SubdomainGroup } from './lib/groupTrainings'
export {
  DESCRIPTION_MAX,
  TITLE_MAX,
  type Domain,
  type Subdomain,
  type Training,
  type TrainingInput,
} from './model/training'
export { TrainingFields } from './ui/TrainingFields'
