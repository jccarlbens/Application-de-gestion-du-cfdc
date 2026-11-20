import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { useState, type FormEvent } from 'react'
import {
  DESCRIPTION_MAX,
  TITLE_MAX,
  addModule,
  assignTrainer,
  fetchModules,
  fetchTrainers,
  trainerLabel,
  updateModule,
  type Module,
  type ModuleInput,
  type Trainer,
} from '../../../entities/training'
import { canRecordTraining, isAdmin, type Viewer } from '../../../entities/viewer'
import { ApiError } from '../../../shared/api'

const inputClass =
  'mt-1 w-full rounded-md border border-brand-100 px-3 py-2 focus:border-brand-600 focus:outline-none focus:ring-2 focus:ring-brand-100'
const primary = 'rounded-md bg-brand-700 px-4 py-2 text-sm font-medium text-white hover:bg-brand-600 disabled:opacity-60'
const secondary = 'rounded-md border border-brand-100 px-4 py-2 text-sm font-medium text-brand-900 hover:bg-brand-50'

function errorText(error: unknown): string | null {
  if (!error) return null
  return error instanceof ApiError ? error.message : 'Le serveur ne répond pas.'
}

function useRefresh(trainingId: string) {
  const queryClient = useQueryClient()
  return () => {
    void queryClient.invalidateQueries({ queryKey: ['modules', trainingId] })
    void queryClient.invalidateQueries({ queryKey: ['history', 'trainings', trainingId] })
  }
}

/** La liste des formateurs proposés. Le formateur actuel reste dans la liste
 *  même s'il est désactivé, pour que l'administrateur puisse le garder. */
function TrainerSelect({
  label,
  value,
  trainers,
  current,
  allowNone,
  onChange,
}: {
  label: string
  value: string
  trainers: readonly Trainer[]
  current?: Trainer | null
  allowNone: boolean
  onChange: (value: string) => void
}) {
  const options = current && !trainers.some((t) => t.id === current.id) ? [current, ...trainers] : trainers
  return (
    <label className="block text-sm font-medium text-brand-900">
      {label}
      <select className={inputClass} value={value} onChange={(event) => onChange(event.target.value)}>
        {allowNone ? <option value="">Formateur à désigner</option> : <option value="">Choisir…</option>}
        {options.map((trainer) => (
          <option key={trainer.id} value={trainer.id}>
            {trainerLabel(trainer)}
          </option>
        ))}
      </select>
    </label>
  )
}

function ModuleFields({
  value,
  trainers,
  current,
  onChange,
}: {
  value: ModuleInput
  trainers: readonly Trainer[]
  current?: Trainer | null
  onChange: (value: ModuleInput) => void
}) {
  return (
    <>
      <label className="block text-sm font-medium text-brand-900">
        Titre du module
        <input
          className={inputClass}
          maxLength={TITLE_MAX}
          value={value.title}
          onChange={(event) => onChange({ ...value, title: event.target.value })}
        />
      </label>
      <TrainerSelect
        label="Formateur"
        value={value.trainerId}
        trainers={trainers}
        current={current}
        allowNone
        onChange={(trainerId) => onChange({ ...value, trainerId })}
      />
      <label className="block text-sm font-medium text-brand-900">
        Description <span className="font-normal">(facultative)</span>
        <textarea
          className={inputClass}
          rows={3}
          maxLength={DESCRIPTION_MAX}
          value={value.description}
          onChange={(event) => onChange({ ...value, description: event.target.value })}
        />
      </label>
    </>
  )
}

function AddModuleForm({ trainingId, trainers, onDone }: { trainingId: string; trainers: readonly Trainer[]; onDone: () => void }) {
  const refresh = useRefresh(trainingId)
  const [value, setValue] = useState<ModuleInput>({ title: '', description: '', trainerId: '' })
  const mutation = useMutation({
    mutationFn: () => addModule(trainingId, value),
    onSuccess: () => {
      refresh()
      onDone()
    },
  })

  function submit(event: FormEvent) {
    event.preventDefault()
    mutation.mutate()
  }

  const error = errorText(mutation.error)
  return (
    <form onSubmit={submit} noValidate className="mt-4 space-y-4 rounded-md border border-brand-100 p-4" aria-label="Ajouter un module">
      <ModuleFields
        value={value}
        trainers={trainers}
        onChange={(next) => {
          setValue(next)
          mutation.reset()
        }}
      />
      {error && (
        <p role="alert" className="text-sm font-medium text-red-700">
          {error}
        </p>
      )}
      <div className="flex flex-wrap gap-3">
        <button type="submit" disabled={!value.title.trim() || mutation.isPending} className={primary}>
          {mutation.isPending ? 'Enregistrement…' : 'Enregistrer le module'}
        </button>
        <button type="button" onClick={onDone} className={secondary}>
          Annuler
        </button>
      </div>
    </form>
  )
}

/** Désigner le formateur d'un module « à désigner » (US-011, décision 1A). */
function AssignForm({ module, trainers, onDone }: { module: Module; trainers: readonly Trainer[]; onDone: () => void }) {
  const refresh = useRefresh(module.trainingId)
  const [trainerId, setTrainerId] = useState('')
  const mutation = useMutation({
    mutationFn: () => assignTrainer(module.id, trainerId),
    onSuccess: () => {
      refresh()
      onDone()
    },
  })

  function submit(event: FormEvent) {
    event.preventDefault()
    mutation.mutate()
  }

  const error = errorText(mutation.error)
  return (
    <form onSubmit={submit} noValidate className="mt-2 space-y-2">
      <TrainerSelect
        label={`Formateur de « ${module.title} »`}
        value={trainerId}
        trainers={trainers}
        allowNone={false}
        onChange={(value) => {
          setTrainerId(value)
          mutation.reset()
        }}
      />
      {error && (
        <p role="alert" className="text-sm font-medium text-red-700">
          {error}
        </p>
      )}
      <div className="flex flex-wrap gap-3">
        <button type="submit" disabled={!trainerId || mutation.isPending} className={primary}>
          Désigner
        </button>
        <button type="button" onClick={onDone} className={secondary}>
          Annuler
        </button>
      </div>
    </form>
  )
}

/** La modification par l'administrateur (affinage de l'Epic 2, Q4). */
function EditModuleForm({ module, trainers, onDone }: { module: Module; trainers: readonly Trainer[]; onDone: () => void }) {
  const refresh = useRefresh(module.trainingId)
  const [value, setValue] = useState<ModuleInput>({
    title: module.title,
    description: module.description ?? '',
    trainerId: module.trainer?.id ?? '',
  })
  const mutation = useMutation({
    mutationFn: () => updateModule(module.id, value),
    onSuccess: () => {
      refresh()
      onDone()
    },
  })

  function submit(event: FormEvent) {
    event.preventDefault()
    mutation.mutate()
  }

  const error = errorText(mutation.error)
  return (
    <form onSubmit={submit} noValidate className="mt-2 space-y-4 rounded-md border border-brand-100 p-4" aria-label={`Modifier « ${module.title} »`}>
      <ModuleFields
        value={value}
        trainers={trainers}
        current={module.trainer}
        onChange={(next) => {
          setValue(next)
          mutation.reset()
        }}
      />
      {error && (
        <p role="alert" className="text-sm font-medium text-red-700">
          {error}
        </p>
      )}
      <div className="flex flex-wrap gap-3">
        <button type="submit" disabled={!value.title.trim() || mutation.isPending} className={primary}>
          {mutation.isPending ? 'Enregistrement…' : 'Enregistrer le module'}
        </button>
        <button type="button" onClick={onDone} className={secondary}>
          Annuler
        </button>
      </div>
    </form>
  )
}

function ModuleItem({ module, viewer, trainers }: { module: Module; viewer: Viewer; trainers: readonly Trainer[] }) {
  const [mode, setMode] = useState<'view' | 'assign' | 'edit'>('view')
  const canAssign = !module.trainer && canRecordTraining(viewer.roles)
  const flagged = module.trainer && (!module.trainer.isActive || !module.trainer.isTrainer)
  return (
    <li className="rounded-md border border-brand-50 px-4 py-3">
      <p className="font-medium text-brand-900">{module.title}</p>
      <p className={`text-sm ${module.trainer && !flagged ? 'text-brand-700' : 'font-medium text-amber-800'}`}>
        {trainerLabel(module.trainer)}
      </p>
      {module.description && <p className="mt-1 whitespace-pre-line text-sm text-brand-900">{module.description}</p>}
      {mode === 'view' && (canAssign || isAdmin(viewer.roles)) && (
        <div className="mt-2 flex flex-wrap gap-3">
          {canAssign && (
            <button type="button" className="text-sm text-brand-700 underline" onClick={() => setMode('assign')}>
              Désigner le formateur
            </button>
          )}
          {isAdmin(viewer.roles) && (
            <button
              type="button"
              className="text-sm text-brand-700 underline"
              aria-label={`Modifier le module « ${module.title} »`}
              onClick={() => setMode('edit')}
            >
              Modifier
            </button>
          )}
        </div>
      )}
      {mode === 'assign' && <AssignForm module={module} trainers={trainers} onDone={() => setMode('view')} />}
      {mode === 'edit' && <EditModuleForm module={module} trainers={trainers} onDone={() => setMode('view')} />}
    </li>
  )
}

/** Les modules d'une formation, sur sa fiche (US-011). */
export function ModulesSection({ trainingId, viewer }: { trainingId: string; viewer: Viewer }) {
  const [adding, setAdding] = useState(false)
  const modules = useQuery({ queryKey: ['modules', trainingId], queryFn: () => fetchModules(trainingId) })
  const canRecord = canRecordTraining(viewer.roles)
  const trainers = useQuery({ queryKey: ['trainers'], queryFn: fetchTrainers, enabled: canRecord })

  return (
    <section aria-labelledby="modules" className="mt-8">
      <div className="mb-3 flex flex-wrap items-center justify-between gap-3">
        <h2 id="modules" className="font-semibold text-brand-900">
          Modules
        </h2>
        {canRecord && !adding && (
          <button type="button" onClick={() => setAdding(true)} className={secondary}>
            Ajouter un module
          </button>
        )}
      </div>
      {modules.isPending && <p className="text-brand-900">Chargement…</p>}
      {modules.isError && <p className="font-medium text-red-700">{errorText(modules.error)}</p>}
      {modules.data && modules.data.length === 0 && !adding && <p className="text-brand-900">Aucun module pour l'instant.</p>}
      {modules.data && modules.data.length > 0 && (
        <ol className="space-y-2">
          {modules.data.map((module) => (
            <ModuleItem key={module.id} module={module} viewer={viewer} trainers={trainers.data ?? []} />
          ))}
        </ol>
      )}
      {adding && <AddModuleForm trainingId={trainingId} trainers={trainers.data ?? []} onDone={() => setAdding(false)} />}
    </section>
  )
}
