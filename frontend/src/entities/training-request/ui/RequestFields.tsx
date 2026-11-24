import { Link } from 'react-router-dom'
import { PERIOD_MAX, SERVICE_MAX, TEXT_MAX, localToday, type TrainingRequestInput } from '../model/trainingRequest'

const inputClass =
  'mt-1 w-full rounded-md border border-brand-100 px-3 py-2 focus:border-brand-600 focus:outline-none focus:ring-2 focus:ring-brand-100'

export type TrainingOption = { id: string; title: string; group: string }

/** Les champs d'une demande de formation, pour l'enregistrer ou l'ajuster. La
 *  liste des formations vient de la page (l'entité ne lit pas le catalogue). */
export function RequestFields({
  value,
  trainings,
  canCreateTraining,
  onChange,
}: {
  value: TrainingRequestInput
  trainings: readonly TrainingOption[]
  canCreateTraining: boolean
  onChange: (value: TrainingRequestInput) => void
}) {
  const groups = [...new Set(trainings.map((t) => t.group))]
  return (
    <>
      <label className="block text-sm font-medium text-brand-900">
        Service demandeur
        <input
          className={inputClass}
          maxLength={SERVICE_MAX}
          value={value.requestingService}
          onChange={(event) => onChange({ ...value, requestingService: event.target.value })}
        />
      </label>
      <fieldset>
        <legend className="text-sm font-medium text-brand-900">Origine</legend>
        <div className="mt-1 flex flex-wrap gap-4 text-sm text-brand-900">
          <label className="flex items-center gap-2">
            <input type="radio" name="origine" checked={!value.isExternal} onChange={() => onChange({ ...value, isExternal: false })} />
            Service de l'AAN
          </label>
          <label className="flex items-center gap-2">
            <input type="radio" name="origine" checked={value.isExternal} onChange={() => onChange({ ...value, isExternal: true })} />
            Entreprise externe
          </label>
        </div>
      </fieldset>
      <div className="grid gap-4 sm:grid-cols-2">
        <label className="block text-sm font-medium text-brand-900">
          Date de réception
          <input
            type="date"
            className={inputClass}
            max={localToday()}
            value={value.receivedOn}
            onChange={(event) => onChange({ ...value, receivedOn: event.target.value })}
          />
        </label>
        <label className="block text-sm font-medium text-brand-900">
          Nombre de participants prévu
          <input
            type="number"
            min={1}
            max={500}
            className={inputClass}
            value={value.expectedParticipants}
            onChange={(event) => onChange({ ...value, expectedParticipants: event.target.value })}
          />
        </label>
      </div>
      <label className="block text-sm font-medium text-brand-900">
        Formation demandée
        <select
          className={inputClass}
          value={value.trainingId}
          onChange={(event) => onChange({ ...value, trainingId: event.target.value })}
        >
          <option value="">Choisir…</option>
          {groups.map((group) => (
            <optgroup key={group} label={group}>
              {trainings
                .filter((t) => t.group === group)
                .map((t) => (
                  <option key={t.id} value={t.id}>
                    {t.title}
                  </option>
                ))}
            </optgroup>
          ))}
        </select>
      </label>
      {canCreateTraining && (
        <p className="text-sm text-brand-900">
          Formation absente du catalogue ?{' '}
          <Link to="/formations/nouvelle" className="text-brand-700 underline">
            Nouvelle formation
          </Link>
        </p>
      )}
      <label className="block text-sm font-medium text-brand-900">
        Période souhaitée <span className="font-normal">(facultative)</span>
        <input
          className={inputClass}
          maxLength={PERIOD_MAX}
          placeholder="par exemple : mars 2027"
          value={value.desiredPeriod}
          onChange={(event) => onChange({ ...value, desiredPeriod: event.target.value })}
        />
      </label>
      <label className="block text-sm font-medium text-brand-900">
        Commentaire <span className="font-normal">(facultatif)</span>
        <textarea
          className={inputClass}
          rows={3}
          maxLength={TEXT_MAX}
          value={value.comment}
          onChange={(event) => onChange({ ...value, comment: event.target.value })}
        />
      </label>
    </>
  )
}
