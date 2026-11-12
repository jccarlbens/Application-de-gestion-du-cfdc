import { useQuery } from '@tanstack/react-query'
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
    <div className="min-h-screen bg-white">
      <header className="bg-brand-700 px-6 py-4 text-white">
        <h1 className="text-xl font-semibold">CFDC — Gestion des formations</h1>
        <p className="text-sm text-brand-100">Autorité Aéroportuaire Nationale</p>
      </header>
      <main className="mx-auto max-w-2xl px-4 py-10">
        <section className="rounded-md border border-brand-100 bg-brand-50 p-6">
          <h2 className="mb-2 text-lg font-semibold text-brand-900">État de l'application</h2>
          <StatusLine />
        </section>
      </main>
    </div>
  )
}
