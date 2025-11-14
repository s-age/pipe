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
  searchL2: (request: SearchL2Request) => Promise<SearchL2Response | undefined>
  getLsData: (request: LsRequest) => Promise<LsResponse | undefined>
} => {
  const actions = useMemo(
    () => ({
      searchL2: async (
        request: SearchL2Request
      ): Promise<SearchL2Response | undefined> => {
        try {
          const result = await fileSearchExplorerApi.searchL2(request)

          return result
        } catch (error: unknown) {
          emitToast.failure((error as Error).message)

          return undefined
        }
      },

      getLsData: async (request: LsRequest): Promise<LsResponse | undefined> => {
        try {
          const result = await fileSearchExplorerApi.getLsData(request)

          return result
        } catch (error: unknown) {
          emitToast.failure((error as Error).message)

          return undefined
        }
      }
    }),
    []
  )

  return actions
}
