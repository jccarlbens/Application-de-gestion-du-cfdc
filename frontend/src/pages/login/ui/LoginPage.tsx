import { useMutation } from '@tanstack/react-query'
import { useState, type FormEvent } from 'react'
import { useNavigate, useSearchParams } from 'react-router-dom'
import { ApiError } from '../../../shared/api'
import { PageShell } from '../../../shared/ui'
import { login } from '../api/login'

const inputClass =
  'mt-1 w-full rounded-md border border-brand-100 px-3 py-2 focus:border-brand-600 focus:outline-none focus:ring-2 focus:ring-brand-100'

export function LoginPage() {
  const navigate = useNavigate()
  const [params] = useSearchParams()
  const [badge, setBadge] = useState('')
  const [password, setPassword] = useState('')
  const mutation = useMutation({
    mutationFn: () => login(badge, password),
    onSuccess: () => navigate('/', { replace: true }),
  })

  function submit(event: FormEvent) {
    event.preventDefault()
    mutation.mutate()
  }

  function edit(setter: (value: string) => void) {
    return (value: string) => {
      setter(value)
      mutation.reset()
    }
  }

  const error =
    mutation.error instanceof ApiError ? mutation.error.message : mutation.error ? 'Le serveur ne répond pas.' : null

  return (
    <PageShell>
      <h1 className="mb-6 text-lg font-semibold text-brand-900">Connexion</h1>
      {params.get('expiree') === '1' && !error && (
        <p className="mb-4 rounded-md bg-brand-50 px-3 py-2 text-sm text-brand-900">
          Votre session a expiré, reconnectez-vous.
        </p>
      )}
      <form onSubmit={submit} noValidate className="space-y-4">
        <label className="block text-sm font-medium text-brand-900">
          Numéro de badge
          <input
            className={inputClass}
            autoComplete="username"
            placeholder="A00-00"
            value={badge}
            onChange={(e) => edit(setBadge)(e.target.value)}
          />
        </label>
        <label className="block text-sm font-medium text-brand-900">
          Mot de passe
          <input
            type="password"
            autoComplete="current-password"
            className={inputClass}
            value={password}
            onChange={(e) => edit(setPassword)(e.target.value)}
          />
        </label>
        {error && (
          <p role="alert" className="text-sm font-medium text-red-700">
            {error}
          </p>
        )}
        <button
          type="submit"
          disabled={mutation.isPending || !badge || !password}
          className="w-full rounded-md bg-brand-700 px-4 py-2 font-medium text-white hover:bg-brand-600 disabled:opacity-60"
        >
          {mutation.isPending ? 'Connexion…' : 'Se connecter'}
        </button>
      </form>
    </PageShell>
  )
}
