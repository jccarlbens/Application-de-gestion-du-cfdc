import { useMutation, useQueryClient } from '@tanstack/react-query'
import { useId, useState, type ChangeEvent } from 'react'
import {
  ACCEPTED_EXTENSIONS,
  MAX_BYTES,
  downloadUrl,
  formatDay,
  formatSize,
  isCurrent,
  replaceDocument,
  uploadDocument,
  type CourseDocument,
} from '../../../entities/document'
import { isAdmin, type Viewer } from '../../../entities/viewer'
import { ApiError } from '../../../shared/api'

function errorText(error: unknown): string | null {
  if (!error) return null
  return error instanceof ApiError ? error.message : 'Le serveur ne répond pas.'
}

/** Choisir un fichier l'envoie aussitôt. La taille est vérifiée ici pour un
 *  message immédiat ; le serveur vérifie tout de nouveau, contenu compris. */
function FilePicker({
  label,
  trainingId,
  send,
}: {
  label: string
  trainingId: string
  send: (file: File) => Promise<CourseDocument>
}) {
  const id = useId()
  const queryClient = useQueryClient()
  const [tooBig, setTooBig] = useState(false)
  const mutation = useMutation({
    mutationFn: send,
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: ['documents', trainingId] })
      void queryClient.invalidateQueries({ queryKey: ['documents'] })
      void queryClient.invalidateQueries({ queryKey: ['history', 'trainings', trainingId] })
    },
  })

  function pick(event: ChangeEvent<HTMLInputElement>) {
    const file = event.target.files?.[0]
    event.target.value = ''
    mutation.reset()
    setTooBig(false)
    if (!file) return
    if (file.size > MAX_BYTES) {
      setTooBig(true)
      return
    }
    mutation.mutate(file)
  }

  const error = tooBig ? 'Le fichier dépasse 25 Mo.' : errorText(mutation.error)
  return (
    <span className="inline-block">
      <label htmlFor={id} className="cursor-pointer text-sm text-brand-700 underline">
        {mutation.isPending ? 'Envoi…' : label}
      </label>
      <input id={id} type="file" accept={ACCEPTED_EXTENSIONS} className="sr-only" onChange={pick} disabled={mutation.isPending} />
      {error && (
        <span role="alert" className="ml-2 text-sm font-medium text-red-700">
          {error}
        </span>
      )}
    </span>
  )
}

function DocumentLine({ document, viewer }: { document: CourseDocument; viewer: Viewer }) {
  const admin = isAdmin(viewer.roles)
  return (
    <li className="flex flex-wrap items-baseline gap-x-3 gap-y-1 text-sm">
      {/* Seuls le formateur du module et l'administrateur ouvrent un document
          (le serveur le vérifie) ; le formateur les ouvre depuis « Mes modules ». */}
      {admin ? (
        <a href={downloadUrl(document.id)} className="font-medium text-brand-700 underline">
          {document.fileName}
        </a>
      ) : (
        <span className="font-medium text-brand-900">{document.fileName}</span>
      )}
      <span className="text-brand-700">
        {formatSize(document.sizeBytes)} · {formatDay(document.uploadedAt)} · {document.uploadedByName}
      </span>
      {admin && isCurrent(document) && (
        <FilePicker
          label={`Remplacer « ${document.fileName} »`}
          trainingId={document.trainingId}
          send={(file) => replaceDocument(document.id, file)}
        />
      )}
    </li>
  )
}

/** Les documents de cours d'un module (US-012). */
export function ModuleDocuments({
  trainingId,
  moduleId,
  documents,
  viewer,
}: {
  trainingId: string
  moduleId: string
  documents: readonly CourseDocument[]
  viewer: Viewer
}) {
  const current = documents.filter(isCurrent)
  const replaced = documents.filter((d) => !isCurrent(d))
  const admin = isAdmin(viewer.roles)
  if (!admin && current.length === 0) return null
  return (
    <div className="mt-3 border-t border-brand-50 pt-2">
      <p className="text-sm font-semibold text-brand-900">Documents</p>
      {current.length === 0 && <p className="text-sm text-brand-900">Aucun document pour l'instant.</p>}
      <ul className="mt-1 space-y-1">
        {current.map((document) => (
          <DocumentLine key={document.id} document={document} viewer={viewer} />
        ))}
      </ul>
      {admin && (
        <p className="mt-2">
          <FilePicker label="Déposer un document" trainingId={trainingId} send={(file) => uploadDocument(moduleId, file)} />
        </p>
      )}
      {admin && replaced.length > 0 && (
        <details className="mt-2">
          <summary className="cursor-pointer text-sm text-brand-700">Versions remplacées ({replaced.length})</summary>
          <ul className="mt-1 space-y-1">
            {replaced.map((document) => (
              <DocumentLine key={document.id} document={document} viewer={viewer} />
            ))}
          </ul>
        </details>
      )}
    </div>
  )
}
