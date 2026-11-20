import { useQuery } from '@tanstack/react-query'
import { fetchModules, fetchTrainers, trainerName } from '../../../entities/training'
import { canRecordTraining, type Viewer } from '../../../entities/viewer'

/** Les modules et les formateurs, pour cette formation : la même requête que
 *  la section, partagée avec l'historique pour nommer les formateurs. */
export function useTrainerNames(trainingId: string, viewer: Viewer): Record<string, string> {
  const modules = useQuery({ queryKey: ['modules', trainingId], queryFn: () => fetchModules(trainingId) })
  const trainers = useQuery({
    queryKey: ['trainers'],
    queryFn: fetchTrainers,
    enabled: canRecordTraining(viewer.roles),
  })
  const names: Record<string, string> = {}
  for (const trainer of trainers.data ?? []) names[trainer.id] = trainerName(trainer)
  for (const module of modules.data ?? []) if (module.trainer) names[module.trainer.id] = trainerName(module.trainer)
  return names
}
