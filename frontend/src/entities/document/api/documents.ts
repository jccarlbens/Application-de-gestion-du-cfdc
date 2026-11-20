import { API_BASE_URL, apiGet, apiPostForm } from '../../../shared/api'
import type { CourseDocument } from '../model/document'

type DocumentDto = {
  id: string
  module_id: string
  module_title: string
  training_id: string
  training_title: string
  file_name: string
  content_type: string
  size_bytes: number
  uploaded_by_name: string
  uploaded_at: string
  replaced_by_id: string | null
}

const toDocument = (dto: DocumentDto): CourseDocument => ({
  id: dto.id,
  moduleId: dto.module_id,
  moduleTitle: dto.module_title,
  trainingId: dto.training_id,
  trainingTitle: dto.training_title,
  fileName: dto.file_name,
  contentType: dto.content_type,
  sizeBytes: dto.size_bytes,
  uploadedByName: dto.uploaded_by_name,
  uploadedAt: dto.uploaded_at,
  replacedById: dto.replaced_by_id,
})

function form(file: File): FormData {
  const data = new FormData()
  data.append('file', file)
  return data
}

export async function fetchTrainingDocuments(trainingId: string): Promise<CourseDocument[]> {
  return (await apiGet<DocumentDto[]>(`/trainings/${encodeURIComponent(trainingId)}/documents`)).map(toDocument)
}

export async function fetchAllDocuments(): Promise<CourseDocument[]> {
  return (await apiGet<DocumentDto[]>('/documents')).map(toDocument)
}

export async function uploadDocument(moduleId: string, file: File): Promise<CourseDocument> {
  return toDocument(await apiPostForm<DocumentDto>(`/modules/${moduleId}/documents`, form(file)))
}

export async function replaceDocument(documentId: string, file: File): Promise<CourseDocument> {
  return toDocument(await apiPostForm<DocumentDto>(`/documents/${documentId}/replace`, form(file)))
}

/** Le lien de téléchargement : le cookie de session l'accompagne (même adresse). */
export function downloadUrl(documentId: string): string {
  return `${API_BASE_URL}/documents/${documentId}/download`
}
