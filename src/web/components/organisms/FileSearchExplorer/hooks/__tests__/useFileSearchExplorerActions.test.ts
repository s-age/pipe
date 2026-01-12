import { renderHook, waitFor } from '@testing-library/react'
import { setupServer } from 'msw/node'

import { fsHandlers, fsErrorHandlers } from '@/msw/resources/fs'
import { clearToasts, getToasts } from '@/stores/useToastStore'

import { useFileSearchExplorerActions } from '../useFileSearchExplorerActions'

const server = setupServer(...fsHandlers)

describe('useFileSearchExplorerActions', () => {
  beforeAll(() => server.listen())
  afterEach(() => {
    server.resetHandlers()
    clearToasts()
  })
  afterAll(() => server.close())

  describe('searchFiles', () => {
    it('should search files successfully and show success toast', async () => {
      const { result } = renderHook(() => useFileSearchExplorerActions())
      const request = { path: 'src', query: 'test' }

      const response = await result.current.searchFiles(request)

      expect(response).toEqual({
        results: [
          {
            filePath: 'src/test.ts',
            lineContent: 'found test',
            lineNumber: 10
          }
        ]
      })

      await waitFor(() => {
        const toasts = getToasts()
        expect(toasts).toHaveLength(1)
        expect(toasts[0].status).toBe('success')
        expect(toasts[0].title).toBe('Search completed successfully')
      })
    })

    it('should handle search files error and show failure toast', async () => {
      server.use(...fsErrorHandlers)
      const { result } = renderHook(() => useFileSearchExplorerActions())
      const request = { path: 'src', query: 'test' }

      const response = await result.current.searchFiles(request)

      expect(response).toBeUndefined()

      await waitFor(() => {
        const toasts = getToasts()
        expect(toasts).toHaveLength(1)
        expect(toasts[0].status).toBe('failure')
        expect(toasts[0].title).toBe('Search failed')
      })
    })
  })

  describe('browseDirectory', () => {
    it('should browse directory successfully', async () => {
      const { result } = renderHook(() => useFileSearchExplorerActions())
      const request = { finalPathList: ['src', 'web'] }

      const response = await result.current.browseDirectory(request)

      expect(response).toEqual({
        entries: [
          {
            isDir: true,
            name: 'subdir',
            path: 'src/web/subdir'
          },
          {
            isDir: false,
            name: 'file.txt',
            path: 'src/web/file.txt',
            size: 1024
          }
        ]
      })

      expect(getToasts()).toHaveLength(0)
    })

    it('should handle browse directory error and show failure toast', async () => {
      server.use(...fsErrorHandlers)
      const { result } = renderHook(() => useFileSearchExplorerActions())
      const request = { finalPathList: ['src', 'web'] }

      const response = await result.current.browseDirectory(request)

      expect(response).toBeUndefined()

      await waitFor(() => {
        const toasts = getToasts()
        expect(toasts).toHaveLength(1)
        expect(toasts[0].status).toBe('failure')
        expect(toasts[0].title).toBe('Failed to list directory')
      })
    })
  })

  describe('hook structure', () => {
    it('should return all action functions', () => {
      const { result } = renderHook(() => useFileSearchExplorerActions())

      expect(result.current).toHaveProperty('searchFiles')
      expect(result.current).toHaveProperty('browseDirectory')
      expect(typeof result.current.searchFiles).toBe('function')
      expect(typeof result.current.browseDirectory).toBe('function')
    })
  })
})
