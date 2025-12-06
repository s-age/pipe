import { client } from '@/lib/api/client' // Corrected path using alias

// Type definitions for searchL2 request and response
export type SearchL2Request = {
  query: string
  path: string
}

export type SearchL2Response = {
  results: {
    filePath: string
    lineNumber: number
    lineContent: string
  }[]
}

// Type definitions for ls request and response
export type LsRequest = {
  finalPathList: string[]
}

export type LsResponse = {
  entries: {
    name: string
    isDir: boolean
    size?: number
    lastModified?: number
    path: string
  }[]
}

export const fileSearchExplorerApi = {
  searchL2: async (request: SearchL2Request): Promise<SearchL2Response> => {
    const response = await client.post<SearchL2Response>('/search_l2', {
      body: request
    })

    return response
  },

  getLsData: async (request: LsRequest): Promise<LsResponse> => {
    const response = await client.post<LsResponse>('/ls', { body: request })

    return response
  }
}
