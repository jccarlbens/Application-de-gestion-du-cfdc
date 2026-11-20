import { useQuery } from '@tanstack/react-query'
import { Link } from 'react-router-dom'
import { downloadUrl, fetchAllDocuments, formatDay, formatSize, isCurrent, type CourseDocument } from '../../../entities/document'
import { isAdmin } from '../../../entities/viewer'
import { ApiError } from '../../../shared/api'
import { AccessDenied } from '../../../shared/ui'
import { AppShell } from '../../../widgets/app-shell'

type TrainingGroup = { id: string; title: string; modules: { id: string; title: string; documents: CourseDocument[] }[] }

/** Par formation, puis par module, dans l'ordre que donne le serveur. */
function group(documents: readonly CourseDocument[]): TrainingGroup[] {
  const trainings: TrainingGroup[] = []
  for (const document of documents.filter(isCurrent)) {
    let training = trainings.find((t) => t.id === document.trainingId)
    if (!training) {
      training = { id: document.trainingId, title: document.trainingTitle, modules: [] }
      trainings.push(training)
    }
    let module = training.modules.find((m) => m.id === document.moduleId)
    if (!module) {
      module = { id: document.moduleId, title: document.moduleTitle, documents: [] }
      training.modules.push(module)
    }
    module.documents.push(document)
  }
  return trainings
}

function DocumentList() {
  const documents = useQuery({ queryKey: ['documents'], queryFn: fetchAllDocuments })
  if (documents.isPending) return <p className="text-brand-900">Chargement des documents…</p>
  if (documents.isError) {
    return (
      <p role="alert" className="font-medium text-red-700">
        {documents.error instanceof ApiError ? documents.error.message : 'Le serveur ne répond pas.'}
      </p>
    )
  }
  const groups = group(documents.data)
  const replaced = documents.data.filter((d) => !isCurrent(d)).length
  if (groups.length === 0) {
    return (
      <p className="text-brand-900">
        Aucun document pour l'instant. On dépose un document dans un module, sur la fiche de sa formation.
      </p>
    )
  }
  return (
    <>
      {groups.map((training) => (
        <section key={training.id} aria-labelledby={`formation-${training.id}`} className="mb-8">
          <h2 id={`formation-${training.id}`} className="mb-2 text-base font-semibold text-brand-900">
            <Link to={`/formations/${training.id}`} className="underline">
              {training.title}
            </Link>
          </h2>
          {training.modules.map((module) => (
            <div key={module.id} className="mb-3 sm:ml-4">
              <h3 className="text-sm font-semibold text-brand-700">{module.title}</h3>
              <ul className="mt-1 space-y-1">
                {module.documents.map((document) => (
                  <li key={document.id} className="flex flex-wrap gap-x-3 text-sm">
                    <a href={downloadUrl(document.id)} className="font-medium text-brand-700 underline">
                      {document.fileName}
                    </a>
                    <span className="text-brand-700">
                      {formatSize(document.sizeBytes)} · {formatDay(document.uploadedAt)} · {document.uploadedByName}
                    </span>
                  </li>
                ))}
              </ul>
            </div>
          ))}
        </section>
      ))}
      {replaced > 0 && (
        <p className="text-sm text-brand-900">
          {replaced} version{replaced > 1 ? 's' : ''} remplacée{replaced > 1 ? 's' : ''} : sur la fiche de chaque formation.
        </p>
      )}
    </>
  )
}

/** Le menu « Documents de cours » (US-012, décision 1A) : tous les documents
 *  en vigueur, par formation puis par module. */
export function DocumentsPage() {
  return (
    <AppShell>
      {(viewer) =>
        isAdmin(viewer.roles) ? (
          <div className="max-w-4xl">
            <h1 className="mb-6 text-lg font-semibold text-brand-900">Documents de cours</h1>
            <DocumentList />
          </div>
        ) : (
          <AccessDenied />
        )
      }
    </AppShell>
  )
}
