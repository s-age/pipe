import { client } from '@/lib/api/client' // Corrected path using alias

// Type definitions for file search request and response
export type FileSearchRequest = {
  query: string
  path: string
}

export type FileSearchResponse = {
  results: {
    filePath: string
    lineNumber: number
    lineContent: string
  }[]
}

// Type definitions for browse request and response
export type BrowseRequest = {
  finalPathList: string[]
}

export type BrowseResponse = {
  entries: {
    name: string
    isDir: boolean
    size?: number
    lastModified?: number
    path: string
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
