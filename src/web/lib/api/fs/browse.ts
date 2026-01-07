import { client } from '@/lib/api/client' // Corrected path using alias

// Type definitions for file search request and response
export type FileSearchRequest = {
  path: string
  query: string
}

export type FileSearchResponse = {
  results: {
    filePath: string
    lineContent: string
    lineNumber: number
  }[]
}

// Type definitions for browse request and response
export type BrowseRequest = {
  finalPathList: string[]
}

export type BrowseResponse = {
  entries: {
    isDir: boolean
    name: string
    path: string
    lastModified?: number
    size?: number
  }[]
}

export const fsApi = {
  searchFiles: async (request: FileSearchRequest): Promise<FileSearchResponse> => {
    const response = await client.post<FileSearchResponse>('/fs/browse_l2', {
      body: request
    })

    return response
  },

  browseDirectory: async (request: BrowseRequest): Promise<BrowseResponse> => {
    const response = await client.post<BrowseResponse>('/fs/browse', { body: request })

    return response
  }
}
