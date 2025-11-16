import { useMemo } from 'react'

import type {
  SearchL2Request,
  LsRequest,
  SearchL2Response,
  LsResponse
} from '@/lib/api/fileSearchExplorer'
import { fileSearchExplorerApi } from '@/lib/api/fileSearchExplorer'
import { emitToast } from '@/lib/toastEvents'

export const useFileSearchExplorerActions = (): {
  searchL2: (request: SearchL2Request) => Promise<SearchL2Response | void>
  getLsData: (request: LsRequest) => Promise<LsResponse | void>
} => {
  const actions = useMemo(
    () => ({
      searchL2: async (request: SearchL2Request): Promise<SearchL2Response | void> => {
        try {
          const result = await fileSearchExplorerApi.searchL2(request)
          emitToast.success('Search completed successfully')

          return result
        } catch (error: unknown) {
          emitToast.failure((error as Error).message || 'Search failed.')
        }
      },

      getLsData: async (request: LsRequest): Promise<LsResponse | void> => {
        try {
          const result = await fileSearchExplorerApi.getLsData(request)

          return result
        } catch (error: unknown) {
          emitToast.failure((error as Error).message || 'Failed to list directory.')
        }
      }
    }),
    []
  )

  return actions
}
