import { useMutation } from '@tanstack/react-query'
import { useState, type FormEvent } from 'react'
import { useSearchParams } from 'react-router-dom'
import { ApiError } from '../../../shared/api'
import { PageShell } from '../../../shared/ui'
import { setPasswordWithLink } from '../api/setPassword'
import { PASSWORD_RULE, checkPassword } from '../model/passwordRule'

const inputClass =
  'mt-1 w-full rounded-md border border-brand-100 px-3 py-2 focus:border-brand-600 focus:outline-none focus:ring-2 focus:ring-brand-100'

export function SetPasswordPage() {
  const [params] = useSearchParams()
  const token = params.get('jeton') ?? ''
  const [password, setPassword] = useState('')
  const [confirmation, setConfirmation] = useState('')
  const [formError, setFormError] = useState<string | null>(null)
  const mutation = useMutation({ mutationFn: () => setPasswordWithLink(token, password) })

  // Dès qu'on corrige un champ, l'ancien message d'erreur disparaît.
  function edit(setter: (value: string) => void) {
    return (value: string) => {
      setter(value)
      setFormError(null)
      mutation.reset()
    }
  }

  if (!token) {
    return (
      <PageShell>
        <h1 className="mb-2 text-lg font-semibold text-brand-900">Lien incomplet</h1>
        <p className="text-red-700">Ce lien ne contient pas de jeton. Ouvrez le lien reçu par email en entier.</p>
      </PageShell>
    )
  }

  if (mutation.isSuccess) {
    return (
      <PageShell>
        <h1 className="mb-2 text-lg font-semibold text-brand-900">Mot de passe enregistré</h1>
        <p className="text-brand-700">Votre mot de passe est enregistré. Vous pourrez vous connecter avec votre numéro de badge.</p>
      </PageShell>
    )
  }

  function submit(event: FormEvent) {
    event.preventDefault()
    const problem = checkPassword(password, confirmation)
    setFormError(problem)
    if (!problem) {
      mutation.mutate()
    }
  }

  const serverError =
    mutation.error instanceof ApiError ? mutation.error.message : mutation.error ? "Le serveur ne répond pas." : null
  const error = formError ?? serverError

  return (
    <PageShell>
      <h1 className="mb-1 text-lg font-semibold text-brand-900">Choisissez votre mot de passe</h1>
      <p className="mb-6 text-sm text-brand-900">{PASSWORD_RULE}</p>
      <form onSubmit={submit} noValidate className="space-y-4">
        <label className="block text-sm font-medium text-brand-900">
          Mot de passe
          <input
            type="password"
            autoComplete="new-password"
            className={inputClass}
            value={password}
            onChange={(e) => edit(setPassword)(e.target.value)}
          />
        </label>
        <label className="block text-sm font-medium text-brand-900">
          Confirmez le mot de passe
          <input
            type="password"
            autoComplete="new-password"
            className={inputClass}
            value={confirmation}
            onChange={(e) => edit(setConfirmation)(e.target.value)}
          />
        </label>
        {error && (
          <p role="alert" className="text-sm font-medium text-red-700">
            {error}
          </p>
        )}
        <button
          type="submit"
          disabled={mutation.isPending}
          className="w-full rounded-md bg-brand-700 px-4 py-2 font-medium text-white hover:bg-brand-600 disabled:opacity-60"
        >
          {mutation.isPending ? 'Enregistrement…' : 'Enregistrer mon mot de passe'}
        </button>
      </form>
    </PageShell>
  )
}
