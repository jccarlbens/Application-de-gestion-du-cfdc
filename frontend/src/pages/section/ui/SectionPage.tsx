import { AppShell, findMenuItem } from '../../../widgets/app-shell'

/** La page d'un menu dont l'écran n'existe pas encore (US-007, décision 2A).
 *  Elle cède la place au vrai écran au fil des user stories. */
export function SectionPage({ menuKey }: { menuKey: string }) {
  const item = findMenuItem(menuKey)
  return (
    <AppShell>
      {(viewer) => {
        if (!item || !item.roles.some((role) => viewer.roles.includes(role))) {
          return (
            <div className="max-w-3xl">
              <h1 className="mb-2 text-lg font-semibold text-brand-900">Accès refusé</h1>
              <p className="text-red-700">Vous n'avez pas accès à cette page.</p>
            </div>
          )
        }
        return (
          <div className="max-w-3xl">
            <h1 className="mb-2 text-lg font-semibold text-brand-900">{item.label}</h1>
            <p className="rounded-md border border-brand-100 bg-brand-50 px-4 py-3 text-brand-900">
              Bientôt disponible.
            </p>
          </div>
        )
      }}
    </AppShell>
  )
}
