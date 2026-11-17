import { useMutation, useQueryClient } from '@tanstack/react-query'
import { useState, type ReactNode } from 'react'
import { NavLink, Navigate, useNavigate } from 'react-router-dom'
import { logout, useViewer, type Viewer } from '../../../entities/viewer'
import { ApiError } from '../../../shared/api'
import { menuFor } from '../model/menu'

const EXPIRED = 'Votre session a expiré, reconnectez-vous.'

/** Le cadre des pages réservées aux personnes connectées : l'en-tête, le menu
 *  de leurs rôles et « Se déconnecter ». Sans session, ramène à la connexion. */
export function AppShell({ children }: { children: (viewer: Viewer) => ReactNode }) {
  const viewer = useViewer()
  const navigate = useNavigate()
  const queryClient = useQueryClient()
  const [menuOpen, setMenuOpen] = useState(false)
  const signOut = useMutation({
    mutationFn: logout,
    onSettled: () => {
      queryClient.clear()
      navigate('/connexion', { replace: true })
    },
  })

  if (viewer.error instanceof ApiError && viewer.error.status === 401) {
    const expired = viewer.error.message === EXPIRED
    return <Navigate to={expired ? '/connexion?expiree=1' : '/connexion'} replace />
  }
  if (viewer.isPending) {
    return <p className="p-6 text-brand-900">Chargement…</p>
  }
  if (viewer.isError) {
    return <p className="p-6 font-medium text-red-700">Le serveur ne répond pas.</p>
  }

  const items = menuFor(viewer.data.roles)
  const linkClass = ({ isActive }: { isActive: boolean }) =>
    `block rounded-md px-3 py-2 text-sm font-medium ${
      isActive ? 'bg-brand-700 text-white' : 'text-brand-900 hover:bg-brand-100'
    }`

  return (
    <div className="min-h-screen bg-white">
      <header className="flex items-center justify-between gap-3 bg-brand-700 px-4 py-3 text-white sm:px-6">
        <div className="flex items-center gap-3">
          <button
            type="button"
            className="rounded-md border border-white/60 px-3 py-1.5 text-sm font-medium lg:hidden"
            aria-expanded={menuOpen}
            aria-controls="menu-principal"
            onClick={() => setMenuOpen((open) => !open)}
          >
            Menu
          </button>
          <NavLink to="/" className="leading-tight">
            <span className="block text-lg font-semibold sm:hidden">CFDC</span>
            <span className="hidden text-xl font-semibold sm:block">CFDC — Gestion des formations</span>
            <span className="hidden text-sm text-brand-100 sm:block">Autorité Aéroportuaire Nationale</span>
          </NavLink>
        </div>
        <button
          type="button"
          onClick={() => signOut.mutate()}
          className="shrink-0 rounded-md border border-white/60 px-3 py-1.5 text-sm font-medium hover:bg-brand-600"
        >
          Se déconnecter
        </button>
      </header>
      <div className="lg:flex">
        <nav
          id="menu-principal"
          aria-label="Menu principal"
          className={`${menuOpen ? 'block' : 'hidden'} border-b border-brand-100 bg-brand-50 p-3 lg:block lg:min-h-[calc(100vh-4.5rem)] lg:w-64 lg:border-r lg:border-b-0`}
        >
          <ul className="space-y-1">
            <li>
              <NavLink to="/" end className={linkClass} onClick={() => setMenuOpen(false)}>
                Accueil
              </NavLink>
            </li>
            {items.map((item) => (
              <li key={item.key}>
                <NavLink to={item.path} className={linkClass} onClick={() => setMenuOpen(false)}>
                  {item.label}
                </NavLink>
              </li>
            ))}
          </ul>
        </nav>
        <main className="flex-1 px-4 py-8 sm:px-8">{children(viewer.data)}</main>
      </div>
    </div>
  )
}
