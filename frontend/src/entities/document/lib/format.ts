/** Une taille lisible, à la française : « 850 Ko », « 2,4 Mo ». */
export function formatSize(bytes: number): string {
  if (bytes < 1024 * 1024) return `${Math.max(1, Math.round(bytes / 1024))} Ko`
  const mo = bytes / (1024 * 1024)
  return `${mo.toLocaleString('fr-FR', { maximumFractionDigits: 1 })} Mo`
}

/** Une date de dépôt : « 20/11/2026 ». */
export function formatDay(iso: string): string {
  return new Intl.DateTimeFormat('fr-FR', { dateStyle: 'short' }).format(new Date(iso))
}
