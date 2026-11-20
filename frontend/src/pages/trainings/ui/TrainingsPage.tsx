import { useQuery } from '@tanstack/react-query'
import { useState } from 'react'
import { Link } from 'react-router-dom'
import { fetchDomains, fetchTrainings, groupTrainings } from '../../../entities/training'
import { canRecordTraining, canSeeCatalogue, isAdmin, type Viewer } from '../../../entities/viewer'
import { ApiError } from '../../../shared/api'
import { AccessDenied } from '../../../shared/ui'
import { AppShell } from '../../../widgets/app-shell'

const buttonClass = 'rounded-md bg-brand-700 px-4 py-2 text-sm font-medium text-white hover:bg-brand-600'

function Catalogue({ viewer }: { viewer: Viewer }) {
  const [domainId, setDomainId] = useState('')
  const trainings = useQuery({ queryKey: ['trainings'], queryFn: fetchTrainings })
  const domains = useQuery({ queryKey: ['domains'], queryFn: fetchDomains })

  if (trainings.isPending) return <p className="text-brand-900">Chargement du catalogue…</p>
  if (trainings.isError) {
    return (
      <p role="alert" className="font-medium text-red-700">
        {trainings.error instanceof ApiError ? trainings.error.message : 'Le serveur ne répond pas.'}
      </p>
    )
  }

  const groups = groupTrainings(trainings.data, domainId || undefined)
  return (
    <>
      <div className="mb-6 flex flex-wrap items-center justify-between gap-3">
        <h1 className="text-lg font-semibold text-brand-900">Formations</h1>
        <div className="flex flex-wrap gap-3">
          {isAdmin(viewer.roles) && (
            <Link
              to="/formations/domaines"
              className="rounded-md border border-brand-100 px-4 py-2 text-sm font-medium text-brand-900 hover:bg-brand-50"
            >
              Domaines et sous-domaines
            </Link>
          )}
          {canRecordTraining(viewer.roles) && (
            <Link to="/formations/nouvelle" className={buttonClass}>
              Nouvelle formation
            </Link>
          )}
        </div>
      </div>

      <label className="mb-6 block max-w-xs text-sm font-medium text-brand-900">
        Domaine
        <select
          className="mt-1 w-full rounded-md border border-brand-100 px-3 py-2"
          value={domainId}
          onChange={(event) => setDomainId(event.target.value)}
        >
          <option value="">Tous les domaines</option>
          {domains.data?.map((domain) => (
            <option key={domain.id} value={domain.id}>
              {domain.name}
            </option>
          ))}
        </select>
      </label>

      {groups.length === 0 && (
        <p className="text-brand-900">
          {domainId ? 'Aucune formation dans ce domaine pour l’instant.' : 'Aucune formation enregistrée pour l’instant.'}
        </p>
      )}
      {groups.map((domain) => (
        <section key={domain.domainId} aria-labelledby={`domaine-${domain.domainId}`} className="mb-8">
          <h2 id={`domaine-${domain.domainId}`} className="mb-3 text-base font-semibold text-brand-900">
            {domain.domainName}
          </h2>
          {domain.subdomains.map((sub) => (
            <div key={sub.subdomainId} className="mb-4 ml-0 sm:ml-4">
              <h3 className="mb-2 text-sm font-semibold text-brand-700">{sub.subdomainName}</h3>
              <ul className="space-y-1">
                {sub.trainings.map((training) => (
                  <li key={training.id}>
                    <Link
                      to={`/formations/${training.id}`}
                      className="block rounded-md border border-brand-50 px-3 py-2 text-brand-900 hover:border-brand-600"
                    >
                      {training.title}
                    </Link>
                  </li>
                ))}
              </ul>
            </div>
          ))}
        </section>
      ))}
    </>
  )
}

export function TrainingsPage() {
  return (
    <AppShell>
      {(viewer) =>
        canSeeCatalogue(viewer.roles) ? (
          <div className="max-w-4xl">
            <Catalogue viewer={viewer} />
          </div>
        ) : (
          <AccessDenied />
        )
      }
    </AppShell>
  )
}
