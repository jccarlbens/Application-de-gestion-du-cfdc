import type { Role } from '../../../entities/viewer'

export type MenuItem = {
  key: string
  label: string
  path: string
  roles: readonly Role[]
}

const EVERYONE_BUT_TRAINER: Role[] = ['secretary', 'coordinator', 'service_head', 'it_admin', 'direction']

// Le tableau des menus validé le 2026-11-17 (US-007), tiré de PRD.md §5. Le
// serveur décide des droits ; ce tableau ne fait que choisir quoi montrer.
export const MENU: readonly MenuItem[] = [
  { key: 'formations', label: 'Formations', path: '/formations', roles: EVERYONE_BUT_TRAINER },
  { key: 'mes-modules', label: 'Mes modules', path: '/mes-modules', roles: ['trainer'] },
  { key: 'demandes', label: 'Demandes de formation', path: '/demandes', roles: EVERYONE_BUT_TRAINER },
  { key: 'sessions', label: 'Sessions et calendrier', path: '/sessions', roles: EVERYONE_BUT_TRAINER },
  { key: 'participants', label: 'Participants', path: '/participants', roles: EVERYONE_BUT_TRAINER },
  { key: 'documents', label: 'Documents de cours', path: '/documents', roles: ['it_admin'] },
  { key: 'corrections', label: 'Demandes de correction', path: '/corrections', roles: ['it_admin'] },
  { key: 'comptes', label: 'Comptes', path: '/comptes', roles: ['coordinator', 'it_admin'] },
  { key: 'vue-ensemble', label: "Vue d'ensemble", path: '/vue-ensemble', roles: ['coordinator', 'service_head', 'it_admin', 'direction'] },
]

/** Les menus d'une personne : l'union des menus de ses rôles, dans l'ordre du tableau. */
export function menuFor(roles: readonly Role[]): MenuItem[] {
  return MENU.filter((item) => item.roles.some((role) => roles.includes(role)))
}

export function findMenuItem(key: string): MenuItem | undefined {
  return MENU.find((item) => item.key === key)
}
