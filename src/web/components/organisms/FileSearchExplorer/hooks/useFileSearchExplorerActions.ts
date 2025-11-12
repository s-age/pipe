import { useMemo } from 'react'

import { useToast } from '@/components/organisms/Toast/hooks/useToast' // Corrected path using alias
import type {
  SearchL2Request,
  LsRequest,
  SearchL2Response,
  LsResponse
} from '@/lib/api/fileSearchExplorer'
import { fileSearchExplorerApi } from '@/lib/api/fileSearchExplorer'

export const useFileSearchExplorerActions = (): {
  searchL2: (request: SearchL2Request) => Promise<SearchL2Response | undefined>
  getLsData: (request: LsRequest) => Promise<LsResponse | undefined>
} => {
  const toast = useToast()

  const actions = useMemo(
    () => ({
      searchL2: async (
        request: SearchL2Request
      ): Promise<SearchL2Response | undefined> => {
        try {
          const result = await fileSearchExplorerApi.searchL2(request)

          // toast.success('Search completed'); // Success toast often not needed
          return result
        } catch (error: unknown) {
          toast.failure((error as Error).message)

          return undefined
        }
      },

      getLsData: async (request: LsRequest): Promise<LsResponse | undefined> => {
        try {
          const result = await fileSearchExplorerApi.getLsData(request)

          return result
        } catch (error: unknown) {
          toast.failure((error as Error).message)

          return undefined
        }
      }
    }),
    // eslint-disable-next-line react-hooks/exhaustive-deps
    []
  )

  return actions
}
