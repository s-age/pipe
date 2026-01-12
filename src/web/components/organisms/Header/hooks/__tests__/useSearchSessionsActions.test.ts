import { renderHook, waitFor } from '@testing-library/react'
import { setupServer } from 'msw/node'

import { fsHandlers, fsErrorHandlers } from '@/msw/resources/fs'
import { clearToasts, getToasts } from '@/stores/useToastStore'

import { useSearchSessionsActions } from '../useSearchSessionsActions'

const server = setupServer(...fsHandlers)

describe('useSearchSessionsActions', () => {
  beforeAll(() => server.listen())
  afterEach(() => {
    server.resetHandlers()
    clearToasts()
  })
  afterAll(() => server.close())

  describe('executeSearch', () => {
    it('should return search results successfully', async () => {
      const { result } = renderHook(() => useSearchSessionsActions())
      const query = 'test'

      const searchResults = await result.current.executeSearch(query)

      expect(searchResults).toHaveLength(3)
      expect(searchResults[0]).toEqual({
        sessionId: 'session-1',
        title: 'test - Session 1'
      })
      expect(getToasts()).toHaveLength(0)
    })

    it('should return empty array when query is empty', async () => {
      const { result } = renderHook(() => useSearchSessionsActions())
      const query = ''

      const searchResults = await result.current.executeSearch(query)

      expect(searchResults).toHaveLength(0)
      expect(getToasts()).toHaveLength(0)
    })

    it('should handle search error and show failure toast', async () => {
      server.use(...fsErrorHandlers)
      const { result } = renderHook(() => useSearchSessionsActions())
      const query = 'test'

      const searchResults = await result.current.executeSearch(query)

      expect(searchResults).toHaveLength(0)
      await waitFor(() => {
        const toasts = getToasts()
        expect(toasts).toHaveLength(1)
        expect(toasts[0].status).toBe('failure')
        expect(toasts[0].title).toBe('Search failed')
      })
    })
  })

  describe('hook structure', () => {
    it('should return executeSearch function', () => {
      const { result } = renderHook(() => useSearchSessionsActions())

      expect(result.current).toHaveProperty('executeSearch')
      expect(typeof result.current.executeSearch).toBe('function')
    })
  })
})
