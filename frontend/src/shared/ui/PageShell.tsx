import type { ReactNode } from 'react'

/** Le cadre de chaque page : l'en-tête bleu de l'application, puis le contenu. */
export function PageShell({ children, aside }: { children: ReactNode; aside?: ReactNode }) {
  return (
    <div className="min-h-screen bg-white">
      <header className="flex items-center justify-between gap-4 bg-brand-700 px-6 py-4 text-white">
        <div>
          <p className="text-xl font-semibold">CFDC — Gestion des formations</p>
          <p className="text-sm text-brand-100">Autorité Aéroportuaire Nationale</p>
        </div>
        {aside}
      </header>
      <main className="mx-auto max-w-md px-4 py-10">{children}</main>
    </div>
  )
}
