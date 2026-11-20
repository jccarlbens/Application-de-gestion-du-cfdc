import { ROLE_LABELS, isRole } from '../../viewer/@x/history'
import type { HistoryEntry } from '../model/history'

export type EntryDescription = {
  /** Ce qui s'est passé, en une phrase. */
  text: string
  /** Vrai quand la phrase ne dit pas tout : « Détails » montre l'avant et l'après. */
  needsDetails: boolean
}

// Les noms des champs, pour « Informations modifiées : … ».
const FIELD_LABELS: Record<string, string> = {
  badge: 'numéro de badge',
  first_name: 'prénom',
  last_name: 'nom',
  email: 'email',
  phone: 'téléphone',
  two_factor_channel: 'canal de double authentification',
}

// Champs techniques qu'on ne raconte pas : ils changent avec d'autres
// (un déblocage remet le compteur d'échecs à zéro, l'intitulé change sa clé).
const SILENT_FIELDS = new Set(['failures_counted_since', 'created_at', 'id', 'title_key'])

function roleLabel(value: unknown): string {
  return typeof value === 'string' && isRole(value) ? ROLE_LABELS[value] : String(value)
}

function changedKeys(entry: HistoryEntry): string[] {
  const before = entry.before ?? {}
  const after = entry.after ?? {}
  return Object.keys(after).filter(
    (key) => !SILENT_FIELDS.has(key) && JSON.stringify(before[key]) !== JSON.stringify(after[key]),
  )
}

function describeAccount(entry: HistoryEntry): EntryDescription | null {
  if (entry.action === 'create') return { text: `Compte créé (${String(entry.after?.badge ?? '')})`, needsDetails: false }
  if (entry.action !== 'update') return null
  const parts: string[] = []
  const others: string[] = []
  for (const key of changedKeys(entry)) {
    const value = entry.after?.[key]
    if (key === 'is_active') parts.push(value ? 'Compte réactivé' : 'Compte désactivé')
    else if (key === 'is_blocked') parts.push(value ? 'Compte bloqué' : 'Compte débloqué')
    else if (key === 'password_hash') parts.push('Mot de passe modifié')
    else others.push(FIELD_LABELS[key] ?? key)
  }
  if (others.length) parts.push(`Informations modifiées : ${others.join(', ')}`)
  return parts.length ? { text: parts.join(' ; '), needsDetails: others.length > 0 } : null
}

function describeTraining(entry: HistoryEntry): EntryDescription | null {
  if (entry.action === 'create') {
    return { text: `Formation créée : « ${String(entry.after?.title ?? '')} »`, needsDetails: false }
  }
  if (entry.action !== 'update') return null
  const parts: string[] = []
  for (const key of changedKeys(entry)) {
    if (key === 'title') parts.push(`Intitulé modifié : « ${String(entry.after?.title ?? '')} »`)
    else if (key === 'description') parts.push('Description modifiée')
    else if (key === 'subdomain_id') parts.push('Sous-domaine modifié')
    else parts.push(`Champ modifié : ${key}`)
  }
  // L'ancien texte et l'ancien sous-domaine ne tiennent pas dans la phrase.
  return parts.length ? { text: parts.join(' ; '), needsDetails: parts.some((p) => !p.startsWith('Intitulé')) } : null
}

function describeNamed(entry: HistoryEntry, kind: 'Domaine' | 'Sous-domaine'): EntryDescription | null {
  const name = String(entry.after?.name ?? '')
  if (entry.action === 'create') return { text: `${kind} créé : « ${name} »`, needsDetails: false }
  if (entry.action === 'update' && changedKeys(entry).includes('name')) {
    return { text: `${kind} renommé : « ${String(entry.before?.name ?? '')} » devient « ${name} »`, needsDetails: false }
  }
  return null
}

/** Une entrée du journal, en phrase lisible (US-009 ; étendu aux formations par US-010). */
export function describeEntry(entry: HistoryEntry): EntryDescription {
  let description: EntryDescription | null = null
  if (entry.tableName === 'user_roles') {
    if (entry.action === 'create') description = { text: `Rôle ajouté : ${roleLabel(entry.after?.role)}`, needsDetails: false }
    if (entry.action === 'delete') description = { text: `Rôle retiré : ${roleLabel(entry.before?.role)}`, needsDetails: false }
  } else if (entry.tableName === 'users') description = describeAccount(entry)
  else if (entry.tableName === 'trainings') description = describeTraining(entry)
  else if (entry.tableName === 'domains') description = describeNamed(entry, 'Domaine')
  else if (entry.tableName === 'subdomains') description = describeNamed(entry, 'Sous-domaine')
  if (description) return description

  const verbs = { create: 'Création', update: 'Modification', delete: 'Suppression' }
  return { text: `${verbs[entry.action]} (${entry.tableName})`, needsDetails: true }
}

/** L'heure d'une entrée, à l'heure de l'appareil : « 17/11/2026 15:21 ». */
export function formatWhen(iso: string): string {
  return new Intl.DateTimeFormat('fr-FR', { dateStyle: 'short', timeStyle: 'short' }).format(new Date(iso))
}
