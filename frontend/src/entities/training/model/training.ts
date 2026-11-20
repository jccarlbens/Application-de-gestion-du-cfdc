export type Subdomain = { id: string; domainId: string; name: string }

export type Domain = { id: string; name: string; subdomains: Subdomain[] }

export type Training = {
  id: string
  title: string
  description: string | null
  subdomainId: string
  subdomainName: string
  domainId: string
  domainName: string
}

export type TrainingInput = { title: string; description: string; subdomainId: string }

// Les limites vérifiées par le serveur (US-010, décision 8), rappelées à l'écran.
export const TITLE_MAX = 200
export const DESCRIPTION_MAX = 2000
