// Les six rôles du personnel du CFDC, et leur nom à l'écran (US-007, décision 5).
export type Role = 'secretary' | 'coordinator' | 'service_head' | 'trainer' | 'it_admin' | 'direction'

export const ROLE_LABELS: Record<Role, string> = {
  secretary: 'Secrétaire',
  coordinator: 'Coordonnateur',
  service_head: 'Chef de service du CFDC',
  trainer: 'Formateur',
  it_admin: 'Administrateur informatique',
  direction: 'Direction du CFDC',
}

const ORDER: Role[] = ['secretary', 'coordinator', 'service_head', 'trainer', 'it_admin', 'direction']

export function isRole(value: string): value is Role {
  return (ORDER as string[]).includes(value)
}

/** Les rôles en français, dans un ordre fixe, séparés par des virgules. */
export function rolesLabel(roles: readonly Role[]): string {
  return ORDER.filter((role) => roles.includes(role))
    .map((role) => ROLE_LABELS[role])
    .join(', ')
}
