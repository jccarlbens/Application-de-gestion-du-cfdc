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

/** Voir la liste des comptes et en créer : administrateur et coordonnateur (PRD.md §5). */
export function canManageAccounts(roles: readonly Role[]): boolean {
  return roles.includes('it_admin') || roles.includes('coordinator')
}

/** Changer les rôles, désactiver, réactiver, débloquer : l'administrateur seul. */
export function isAdmin(roles: readonly Role[]): boolean {
  return roles.includes('it_admin')
}

/** Les rôles proposés à la création : le coordonnateur ne donne pas le rôle
 *  d'administrateur (US-002, décision 4A). */
export function grantableRoles(roles: readonly Role[]): Role[] {
  return isAdmin(roles) ? [...ORDER] : ORDER.filter((role) => role !== 'it_admin')
}

export const ALL_ROLES: readonly Role[] = ORDER
