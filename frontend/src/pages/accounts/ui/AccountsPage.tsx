import { useQuery } from '@tanstack/react-query'
import { Link } from 'react-router-dom'
import { StatusBadge, accountStatus, byLastName, fetchAccounts } from '../../../entities/account'
import { canManageAccounts, rolesLabel } from '../../../entities/viewer'
import { ApiError } from '../../../shared/api'
import { AccessDenied } from '../../../shared/ui'
import { AppShell } from '../../../widgets/app-shell'

function AccountList() {
  const accounts = useQuery({ queryKey: ['accounts'], queryFn: fetchAccounts })

  if (accounts.isPending) return <p className="text-brand-900">Chargement des comptes…</p>
  if (accounts.isError) {
    return (
      <p role="alert" className="font-medium text-red-700">
        {accounts.error instanceof ApiError ? accounts.error.message : 'Le serveur ne répond pas.'}
      </p>
    )
  }

  const sorted = [...accounts.data].sort(byLastName)
  return (
    <>
      {/* Sur ordinateur : un tableau. */}
      <table className="hidden w-full border-collapse text-left text-sm md:table">
        <thead>
          <tr className="border-b border-brand-100 text-brand-900">
            <th className="py-2 pr-4 font-semibold">Numéro de badge</th>
            <th className="py-2 pr-4 font-semibold">Nom</th>
            <th className="py-2 pr-4 font-semibold">Prénom</th>
            <th className="py-2 pr-4 font-semibold">Rôles</th>
            <th className="py-2 font-semibold">Statut</th>
          </tr>
        </thead>
        <tbody>
          {sorted.map((account) => (
            <tr key={account.id} className="border-b border-brand-50 hover:bg-brand-50">
              <td className="py-2 pr-4">
                <Link to={`/comptes/${account.badge}`} className="font-medium text-brand-700 underline">
                  {account.badge}
                </Link>
              </td>
              <td className="py-2 pr-4">{account.lastName}</td>
              <td className="py-2 pr-4">{account.firstName}</td>
              <td className="py-2 pr-4">{rolesLabel(account.roles)}</td>
              <td className="py-2">
                <StatusBadge status={accountStatus(account)} />
              </td>
            </tr>
          ))}
        </tbody>
      </table>

      {/* Sur téléphone : une carte par compte. */}
      <ul className="space-y-3 md:hidden" aria-label="Comptes">
        {sorted.map((account) => (
          <li key={account.id}>
            <Link
              to={`/comptes/${account.badge}`}
              className="block rounded-md border border-brand-100 p-4 hover:border-brand-600"
            >
              <span className="flex items-center justify-between gap-2">
                <span className="font-semibold text-brand-900">
                  {account.lastName} {account.firstName}
                </span>
                <StatusBadge status={accountStatus(account)} />
              </span>
              <span className="block text-sm text-brand-700">{account.badge}</span>
              <span className="block text-sm text-brand-900">{rolesLabel(account.roles)}</span>
            </Link>
          </li>
        ))}
      </ul>
    </>
  )
}

export function AccountsPage() {
  return (
    <AppShell>
      {(viewer) =>
        canManageAccounts(viewer.roles) ? (
          <div className="max-w-5xl">
            <div className="mb-6 flex flex-wrap items-center justify-between gap-3">
              <h1 className="text-lg font-semibold text-brand-900">Comptes</h1>
              <Link
                to="/comptes/nouveau"
                className="rounded-md bg-brand-700 px-4 py-2 text-sm font-medium text-white hover:bg-brand-600"
              >
                Nouveau compte
              </Link>
            </div>
            <AccountList />
          </div>
        ) : (
          <AccessDenied />
        )
      }
    </AppShell>
  )
}
