import { useMemo } from 'react'

import type {
  SearchL2Request,
  LsRequest,
  SearchL2Response,
  LsResponse
} from '@/lib/api/fileSearchExplorer'
import { fileSearchExplorerApi } from '@/lib/api/fileSearchExplorer'
import { addToast } from '@/stores/useToastStore'

export const useFileSearchExplorerActions = (): {
  searchL2: (request: SearchL2Request) => Promise<SearchL2Response | void>
  getLsData: (request: LsRequest) => Promise<LsResponse | void>
} => {
  const actions = useMemo(
    () => ({
      searchL2: async (request: SearchL2Request): Promise<SearchL2Response | void> => {
        try {
          const result = await fileSearchExplorerApi.searchL2(request)
          addToast({ status: 'success', title: 'Search completed successfully' })

          return result
        } catch (error: unknown) {
          addToast({
            status: 'failure',
            title: (error as Error).message || 'Search failed.'
          })
        }
      },

      getLsData: async (request: LsRequest): Promise<LsResponse | void> => {
        try {
          const result = await fileSearchExplorerApi.getLsData(request)

          return result
        } catch (error: unknown) {
          addToast({
            status: 'failure',
            title: (error as Error).message || 'Failed to list directory.'
          })
        }
      }
    }),
    []
  )

  return actions
}
