import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { Navigate, useNavigate } from 'react-router-dom'
import { ApiError } from '../../../shared/api'
import { PageShell } from '../../../shared/ui'
import { fetchHealth } from '../api/health'
import { fetchMe, logout } from '../api/session'

const EXPIRED = 'Votre session a expiré, reconnectez-vous.'

function StatusLine() {
  const { data, isPending, isError } = useQuery({ queryKey: ['health'], queryFn: fetchHealth })

  if (isPending) {
    return <p className="text-brand-900">Vérification du serveur…</p>
  }
  if (isError) {
    return <p className="font-medium text-red-700">Le serveur ne répond pas.</p>
  }
  return data.isDatabaseReachable ? (
    <p className="font-medium text-brand-700">Le serveur et la base de données répondent.</p>
  ) : (
    <p className="font-medium text-red-700">Le serveur répond, mais la base de données est injoignable.</p>
  )
}

export function HomePage() {
  const navigate = useNavigate()
  const queryClient = useQueryClient()
  const me = useQuery({ queryKey: ['me'], queryFn: fetchMe, retry: false })
  const signOut = useMutation({
    mutationFn: logout,
    onSettled: () => {
      queryClient.clear()
      navigate('/connexion', { replace: true })
    },
  })

  if (me.error instanceof ApiError && me.error.status === 401) {
    const expired = me.error.message === EXPIRED
    return <Navigate to={expired ? '/connexion?expiree=1' : '/connexion'} replace />
  }

  const aside = me.data && (
    <button
      type="button"
      onClick={() => signOut.mutate()}
      className="rounded-md border border-white/60 px-3 py-1.5 text-sm font-medium text-white hover:bg-brand-600"
    >
      Se déconnecter
    </button>
  )

  return (
    <PageShell aside={aside}>
      {me.isPending && <p className="text-brand-900">Chargement…</p>}
      {me.isError && !(me.error instanceof ApiError && me.error.status === 401) && (
        <p className="font-medium text-red-700">Le serveur ne répond pas.</p>
      )}
      {me.data && (
        <>
          <h1 className="mb-6 text-lg font-semibold text-brand-900">
            Connecté : {me.data.fullName} ({me.data.badge})
          </h1>
          <section className="rounded-md border border-brand-100 bg-brand-50 p-6">
            <h2 className="mb-2 text-lg font-semibold text-brand-900">État de l'application</h2>
            <StatusLine />
          </section>
        </>
      )}
    </PageShell>
  )
}
