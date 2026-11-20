import { useQuery } from '@tanstack/react-query'
import { downloadUrl, formatDay, formatSize } from '../../../entities/document'
import { fetchMyModules, type MyTraining } from '../../../entities/training'
import { isTrainer } from '../../../entities/viewer'
import { ApiError } from '../../../shared/api'
import { AccessDenied } from '../../../shared/ui'
import { AppShell } from '../../../widgets/app-shell'

function TrainingCard({ training }: { training: MyTraining }) {
  return (
    <section aria-labelledby={`formation-${training.id}`} className="mb-8 rounded-md border border-brand-100 p-4">
      <h2 id={`formation-${training.id}`} className="text-base font-semibold text-brand-900">
        {training.title}
      </h2>
      <p className="text-sm text-brand-700">
        {training.domainName} › {training.subdomainName}
      </p>
      {training.description && <p className="mt-2 whitespace-pre-line text-sm text-brand-900">{training.description}</p>}
      <ol className="mt-4 space-y-3">
        {training.modules.map((module) => (
          <li key={module.id} className="border-l-2 border-brand-100 pl-3">
            <h3 className="font-medium text-brand-900">{module.title}</h3>
            {module.description && <p className="whitespace-pre-line text-sm text-brand-900">{module.description}</p>}
            {module.documents.length === 0 ? (
              <p className="mt-1 text-sm text-brand-700">Pas encore de document pour ce module.</p>
            ) : (
              <ul className="mt-1 space-y-1" aria-label={`Documents de « ${module.title} »`}>
                {module.documents.map((document) => (
                  <li key={document.id} className="flex flex-wrap gap-x-3 text-sm">
                    <a href={downloadUrl(document.id)} className="font-medium text-brand-700 underline">
                      {document.fileName}
                    </a>
                    <span className="text-brand-700">
                      {formatSize(document.sizeBytes)} · {formatDay(document.uploadedAt)}
                    </span>
                  </li>
                ))}
              </ul>
            )}
          </li>
        ))}
      </ol>
    </section>
  )
}

function MyModules() {
  const trainings = useQuery({ queryKey: ['my-modules'], queryFn: fetchMyModules })
  if (trainings.isPending) return <p className="text-brand-900">Chargement de vos modules…</p>
  if (trainings.isError) {
    return (
      <p role="alert" className="font-medium text-red-700">
        {trainings.error instanceof ApiError ? trainings.error.message : 'Le serveur ne répond pas.'}
      </p>
    )
  }
  if (trainings.data.length === 0) return <p className="text-brand-900">Aucun module ne vous est confié pour l'instant.</p>
  return (
    <>
      {trainings.data.map((training) => (
        <TrainingCard key={training.id} training={training} />
      ))}
    </>
  )
}

/** « Mes modules » (US-013) : les modules du formateur et leurs documents. */
export function MyModulesPage() {
  return (
    <AppShell>
      {(viewer) =>
        isTrainer(viewer.roles) ? (
          <div className="max-w-3xl">
            <h1 className="mb-6 text-lg font-semibold text-brand-900">Mes modules</h1>
            <MyModules />
          </div>
        ) : (
          <AccessDenied />
        )
      }
    </AppShell>
  )
}
