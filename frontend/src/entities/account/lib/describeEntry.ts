import { ROLE_LABELS, isRole } from '../../viewer/@x/account'
import type { HistoryEntry } from '../model/account'

// Les noms des champs d'un compte, pour « Informations modifiées : … ».
const FIELD_LABELS: Record<string, string> = {
  badge: 'numéro de badge',
  first_name: 'prénom',
  last_name: 'nom',
  email: 'email',
  phone: 'téléphone',
  two_factor_channel: 'canal de double authentification',
}

// Champs techniques qu'on ne raconte pas : ils changent avec d'autres
// (un déblocage remet le compteur d'échecs à zéro).
const SILENT_FIELDS = new Set(['failures_counted_since', 'created_at', 'id'])

export type EntryDescription = {
  /** Ce qui s'est passé, en une phrase. */
  text: string
  /** Vrai quand la phrase ne dit pas tout : « Détails » montre l'avant et l'après. */
  needsDetails: boolean
}

function roleLabel(value: unknown): string {
  return typeof value === 'string' && isRole(value) ? ROLE_LABELS[value] : String(value)
}

function changedKeys(entry: HistoryEntry): string[] {
  const before = entry.before ?? {}
  const after = entry.after ?? {}
  return Object.keys(after).filter((key) => JSON.stringify(before[key]) !== JSON.stringify(after[key]))
}

/** Une entrée du journal, en phrase lisible (US-009, décision 5). */
export function describeEntry(entry: HistoryEntry): EntryDescription {
  if (entry.tableName === 'user_roles') {
    if (entry.action === 'create') return { text: `Rôle ajouté : ${roleLabel(entry.after?.role)}`, needsDetails: false }
    if (entry.action === 'delete') return { text: `Rôle retiré : ${roleLabel(entry.before?.role)}`, needsDetails: false }
  }

  if (entry.tableName === 'users') {
    if (entry.action === 'create') {
      return { text: `Compte créé (${String(entry.after?.badge ?? '')})`, needsDetails: false }
    }
    if (entry.action === 'update') {
      const parts: string[] = []
      const others: string[] = []
      for (const key of changedKeys(entry)) {
        const value = entry.after?.[key]
        if (key === 'is_active') parts.push(value ? 'Compte réactivé' : 'Compte désactivé')
        else if (key === 'is_blocked') parts.push(value ? 'Compte bloqué' : 'Compte débloqué')
        else if (key === 'password_hash') parts.push('Mot de passe modifié')
        else if (!SILENT_FIELDS.has(key)) others.push(FIELD_LABELS[key] ?? key)
      }
      if (others.length) parts.push(`Informations modifiées : ${others.join(', ')}`)
      if (parts.length) return { text: parts.join(' ; '), needsDetails: others.length > 0 }
    }
  }

  const verbs = { create: 'Création', update: 'Modification', delete: 'Suppression' }
  return { text: `${verbs[entry.action]} (${entry.tableName})`, needsDetails: true }
}

/** L'heure d'une entrée, à l'heure de l'appareil : « 17/11/2026 15:21 ». */
export function formatWhen(iso: string): string {
  return new Intl.DateTimeFormat('fr-FR', { dateStyle: 'short', timeStyle: 'short' }).format(new Date(iso))
}
