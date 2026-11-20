import { useQuery } from '@tanstack/react-query'
import { fetchModules, fetchTrainers, trainerName } from '../../../entities/training'
import { canRecordTraining, type Viewer } from '../../../entities/viewer'

/** Les noms connus de la fiche (formateurs, modules), pour que l'historique
 *  les nomme. Mêmes requêtes que la section « Modules » : rien n'est chargé deux fois. */
export function useHistoryNames(trainingId: string, viewer: Viewer): Record<string, string> {
  const modules = useQuery({ queryKey: ['modules', trainingId], queryFn: () => fetchModules(trainingId) })
  const trainers = useQuery({
    queryKey: ['trainers'],
    queryFn: fetchTrainers,
    enabled: canRecordTraining(viewer.roles),
  })
  const names: Record<string, string> = {}
  for (const trainer of trainers.data ?? []) names[trainer.id] = trainerName(trainer)
  for (const module of modules.data ?? []) {
    // Le titre d'un module, pour nommer le module d'un document (US-012).
    names[module.id] = module.title
    if (module.trainer) names[module.trainer.id] = trainerName(module.trainer)
  }
  return names
}
