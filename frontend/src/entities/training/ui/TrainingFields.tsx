import { DESCRIPTION_MAX, TITLE_MAX, type Domain, type TrainingInput } from '../model/training'

const inputClass =
  'mt-1 w-full rounded-md border border-brand-100 px-3 py-2 focus:border-brand-600 focus:outline-none focus:ring-2 focus:ring-brand-100'

/** Les champs d'une formation, pour la créer ou la modifier. Le sous-domaine se
 *  choisit dans une liste regroupée par domaine. */
export function TrainingFields({
  value,
  domains,
  onChange,
}: {
  value: TrainingInput
  domains: readonly Domain[]
  onChange: (value: TrainingInput) => void
}) {
  return (
    <>
      <label className="block text-sm font-medium text-brand-900">
        Intitulé
        <input
          className={inputClass}
          maxLength={TITLE_MAX}
          value={value.title}
          onChange={(event) => onChange({ ...value, title: event.target.value })}
        />
      </label>
      <label className="block text-sm font-medium text-brand-900">
        Sous-domaine
        <select
          className={inputClass}
          value={value.subdomainId}
          onChange={(event) => onChange({ ...value, subdomainId: event.target.value })}
        >
          <option value="">Choisir…</option>
          {domains.map((domain) => (
            <optgroup key={domain.id} label={domain.name}>
              {domain.subdomains.map((sub) => (
                <option key={sub.id} value={sub.id}>
                  {sub.name}
                </option>
              ))}
            </optgroup>
          ))}
        </select>
      </label>
      <label className="block text-sm font-medium text-brand-900">
        Description <span className="font-normal">(facultative)</span>
        <textarea
          className={inputClass}
          rows={4}
          maxLength={DESCRIPTION_MAX}
          value={value.description}
          onChange={(event) => onChange({ ...value, description: event.target.value })}
        />
      </label>
    </>
  )
}
