import { useQuery } from '@tanstack/react-query'
import { Link } from 'react-router-dom'
import { rolesLabel } from '../../../entities/viewer'
import { AppShell, menuFor } from '../../../widgets/app-shell'
import { fetchHealth } from '../api/health'

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
  return (
    <AppShell>
      {(viewer) => (
        <div className="max-w-3xl">
          <h1 className="text-lg font-semibold text-brand-900">
            Connecté : {viewer.fullName} ({viewer.badge})
          </h1>
          <p className="mb-6 text-sm text-brand-900">Rôles : {rolesLabel(viewer.roles)}</p>

          <h2 className="mb-3 font-semibold text-brand-900">Accès rapide</h2>
          <ul className="mb-8 grid gap-3 sm:grid-cols-2">
            {menuFor(viewer.roles).map((item) => (
              <li key={item.key}>
                <Link
                  to={item.path}
                  className="block rounded-md border border-brand-100 bg-white px-4 py-3 font-medium text-brand-700 hover:border-brand-600 hover:bg-brand-50"
                >
                  {item.label}
                </Link>
              </li>
            ))}
          </ul>

          <section className="rounded-md border border-brand-100 bg-brand-50 p-6">
            <h2 className="mb-2 font-semibold text-brand-900">État de l'application</h2>
            <StatusLine />
          </section>
        </div>
      )}
    </AppShell>
  )
}
