import { useEffect, useRef, type ReactNode } from 'react'

/** Une fenêtre de confirmation avant une action importante (US-009). Elle
 *  s'ouvre en fenêtre modale du navigateur : le clavier y reste, et Échap
 *  annule. */
export function ConfirmDialog({
  open,
  title,
  children,
  confirmLabel,
  danger = false,
  pending = false,
  error,
  onConfirm,
  onCancel,
}: {
  open: boolean
  title: string
  children?: ReactNode
  confirmLabel: string
  danger?: boolean
  pending?: boolean
  error?: string | null
  onConfirm: () => void
  onCancel: () => void
}) {
  const ref = useRef<HTMLDialogElement>(null)

  useEffect(() => {
    const dialog = ref.current
    if (!dialog) return
    if (open && !dialog.open) dialog.showModal?.()
    if (!open && dialog.open) dialog.close?.()
  }, [open])

  if (!open) return null

  return (
    <dialog
      ref={ref}
      open
      aria-labelledby="confirm-title"
      onCancel={(event) => {
        event.preventDefault()
        onCancel()
      }}
      className="fixed inset-0 m-auto w-[min(28rem,calc(100%-2rem))] rounded-md border border-brand-100 bg-white p-6 shadow-xl backdrop:bg-brand-900/40"
    >
      <h2 id="confirm-title" className="mb-2 text-lg font-semibold text-brand-900">
        {title}
      </h2>
      {children && <div className="mb-4 text-sm text-brand-900">{children}</div>}
      {error && (
        <p role="alert" className="mb-4 text-sm font-medium text-red-700">
          {error}
        </p>
      )}
      <div className="flex justify-end gap-3">
        <button
          type="button"
          onClick={onCancel}
          className="rounded-md border border-brand-100 px-4 py-2 text-sm font-medium text-brand-900 hover:bg-brand-50"
        >
          Annuler
        </button>
        <button
          type="button"
          onClick={onConfirm}
          disabled={pending}
          className={`rounded-md px-4 py-2 text-sm font-medium text-white disabled:opacity-60 ${
            danger ? 'bg-red-700 hover:bg-red-600' : 'bg-brand-700 hover:bg-brand-600'
          }`}
        >
          {pending ? 'Un instant…' : confirmLabel}
        </button>
      </div>
    </dialog>
  )
}
