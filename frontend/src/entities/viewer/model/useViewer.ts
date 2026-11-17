import { useQuery } from '@tanstack/react-query'
import { fetchViewer } from '../api/viewer'

export const VIEWER_QUERY_KEY = ['viewer']

export function useViewer() {
  return useQuery({ queryKey: VIEWER_QUERY_KEY, queryFn: fetchViewer, retry: false })
}
