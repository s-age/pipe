import { client } from '@/lib/api/client' // Corrected path using alias

// Type definitions for searchL2 request and response
export type SearchL2Request = {
  query: string
  path: string
}

export type SearchL2Response = {
  results: {
    file_path: string
    line_number: number
    line_content: string
  }[]
}

// Type definitions for ls request and response
export type LsRequest = {
  final_path_list: string[]
}

export type LsResponse = {
  entries: {
    name: string
    is_dir: boolean
    size?: number
    last_modified?: number
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
