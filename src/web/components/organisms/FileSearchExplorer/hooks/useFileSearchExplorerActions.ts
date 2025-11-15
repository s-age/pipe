import { useMemo } from 'react'

import type {
  SearchL2Request,
  LsRequest,
  SearchL2Response,
  LsResponse
} from '@/lib/api/fileSearchExplorer'
import { fileSearchExplorerApi } from '@/lib/api/fileSearchExplorer'

export const useFileSearchExplorerActions = (): {
  searchL2: (request: SearchL2Request) => Promise<SearchL2Response>
  getLsData: (request: LsRequest) => Promise<LsResponse>
} => {
  const actions = useMemo(
    () => ({
      searchL2: async (request: SearchL2Request): Promise<SearchL2Response> => {
        const result = await fileSearchExplorerApi.searchL2(request)

        return result
      },

      getLsData: async (request: LsRequest): Promise<LsResponse> => {
        const result = await fileSearchExplorerApi.getLsData(request)

        return result
      }
    }),
    []
  )

  return actions
}
