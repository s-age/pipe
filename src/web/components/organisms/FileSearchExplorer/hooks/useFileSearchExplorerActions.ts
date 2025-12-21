import { useCallback } from 'react'

import type {
  FileSearchRequest,
  BrowseRequest,
  FileSearchResponse,
  BrowseResponse
} from '@/lib/api/fs/browse'
import { fsApi } from '@/lib/api/fs/browse'
import { addToast } from '@/stores/useToastStore'

export const useFileSearchExplorerActions = (): {
  searchFiles: (request: FileSearchRequest) => Promise<FileSearchResponse | void>
  browseDirectory: (request: BrowseRequest) => Promise<BrowseResponse | void>
} => {
  const searchFiles = useCallback(
    async (request: FileSearchRequest): Promise<FileSearchResponse | void> => {
      try {
        const result = await fsApi.searchFiles(request)
        addToast({ status: 'success', title: 'Search completed successfully' })

        return result
      } catch (error: unknown) {
        addToast({
          status: 'failure',
          title: (error as Error).message || 'Search failed.'
        })
      }
    },
    []
  )

  const browseDirectory = useCallback(
    async (request: BrowseRequest): Promise<BrowseResponse | void> => {
      try {
        const result = await fsApi.browseDirectory(request)

        return result
      } catch (error: unknown) {
        addToast({
          status: 'failure',
          title: (error as Error).message || 'Failed to list directory.'
        })
      }
    },
    []
  )

  return { searchFiles, browseDirectory }
}
