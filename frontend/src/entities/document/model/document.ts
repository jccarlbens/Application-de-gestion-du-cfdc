export type CourseDocument = {
  id: string
  moduleId: string
  moduleTitle: string
  trainingId: string
  trainingTitle: string
  fileName: string
  contentType: string
  sizeBytes: number
  uploadedByName: string
  uploadedAt: string
  replacedById: string | null
}

// Ce que le serveur accepte (US-012) ; il vérifie de nouveau, contenu compris.
export const ACCEPTED_EXTENSIONS = '.pdf,.doc,.docx,.ppt,.pptx'
export const MAX_BYTES = 25 * 1024 * 1024

export function isCurrent(document: CourseDocument): boolean {
  return document.replacedById === null
}
