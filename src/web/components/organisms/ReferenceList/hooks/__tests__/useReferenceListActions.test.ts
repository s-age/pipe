import { renderHook, waitFor } from '@testing-library/react'
import { setupServer } from 'msw/node'

import { fsHandlers, fsErrorHandlers } from '@/msw/resources/fs'
import { metaHandlers, metaErrorHandlers } from '@/msw/resources/meta'
import { sessionHandlers } from '@/msw/resources/session'
import { clearToasts, getToasts } from '@/stores/useToastStore'
import type { Reference } from '@/types/reference'

import { useReferenceListActions } from '../useReferenceListActions'

const server = setupServer(...fsHandlers, ...metaHandlers, ...sessionHandlers)

describe('useReferenceListActions', () => {
  beforeAll(() => server.listen())
  afterEach(() => {
    server.resetHandlers()
    clearToasts()
  })
  afterAll(() => server.close())

  const mockSessionId = 'test-session-id'

  describe('handleUpdateReference', () => {
    const newReferences: Reference[] = [
      {
        path: 'src/test.ts'
      }
    ]

    it('should update references successfully and show success toast', async () => {
      const { result } = renderHook(() => useReferenceListActions(mockSessionId))

      const updatedReferences =
        await result.current.handleUpdateReference(newReferences)

      await waitFor(() => {
        const toasts = getToasts()
        expect(toasts).toHaveLength(1)
        expect(toasts[0].status).toBe('success')
        expect(toasts[0].title).toBe('Reference added successfully')
      })
      expect(updatedReferences).toEqual([]) // sessionHandlers returns empty references by default
    })

    it('should handle update reference error and show failure toast', async () => {
      server.use(...metaErrorHandlers)
      const { result } = renderHook(() => useReferenceListActions(mockSessionId))

      await result.current.handleUpdateReference(newReferences)

      await waitFor(() => {
        const toasts = getToasts()
        expect(toasts).toHaveLength(1)
        expect(toasts[0].status).toBe('failure')
        expect(toasts[0].title).toBe('Failed to add reference.')
      })
    })

    it('should return early if currentSessionId is null', async () => {
      const { result } = renderHook(() => useReferenceListActions(null))

      const updatedReferences =
        await result.current.handleUpdateReference(newReferences)

      expect(updatedReferences).toBeUndefined()
      expect(getToasts()).toHaveLength(0)
    })
  })

  describe('loadRootSuggestions', () => {
    it('should load root suggestions successfully', async () => {
      const { result } = renderHook(() => useReferenceListActions(mockSessionId))

      const suggestions = await result.current.loadRootSuggestions()

      expect(suggestions).toHaveLength(2)
      expect(suggestions[0]).toEqual({ name: 'subdir', isDirectory: true })
      expect(suggestions[1]).toEqual({ name: 'file.txt', isDirectory: false })
    })

    it('should handle load root suggestions error and show failure toast', async () => {
      server.use(...fsErrorHandlers)
      const { result } = renderHook(() => useReferenceListActions(mockSessionId))

      const suggestions = await result.current.loadRootSuggestions()

      await waitFor(() => {
        const toasts = getToasts()
        expect(toasts).toHaveLength(1)
        expect(toasts[0].status).toBe('failure')
        expect(toasts[0].title).toBe('Failed to list directory')
      })
      expect(suggestions).toEqual([])
    })

    it('should return empty array if currentSessionId is null', async () => {
      const { result } = renderHook(() => useReferenceListActions(null))

      const suggestions = await result.current.loadRootSuggestions()

      expect(suggestions).toEqual([])
      expect(getToasts()).toHaveLength(0)
    })
  })

  describe('loadSubDirectorySuggestions', () => {
    it('should load sub-directory suggestions successfully', async () => {
      const { result } = renderHook(() => useReferenceListActions(mockSessionId))

      const suggestions = await result.current.loadSubDirectorySuggestions(['src'])

      expect(suggestions).toHaveLength(2)
      expect(suggestions[0]).toEqual({ name: 'subdir', isDirectory: true })
    })

    it('should handle load sub-directory suggestions error and show failure toast', async () => {
      server.use(...fsErrorHandlers)
      const { result } = renderHook(() => useReferenceListActions(mockSessionId))

      const suggestions = await result.current.loadSubDirectorySuggestions(['src'])

      await waitFor(() => {
        const toasts = getToasts()
        expect(toasts).toHaveLength(1)
        expect(toasts[0].status).toBe('failure')
        expect(toasts[0].title).toBe('Failed to list directory')
      })
      expect(suggestions).toEqual([])
    })
  })

  describe('hook structure', () => {
    it('should return all action functions', () => {
      const { result } = renderHook(() => useReferenceListActions(mockSessionId))

      expect(result.current).toHaveProperty('handleUpdateReference')
      expect(result.current).toHaveProperty('loadRootSuggestions')
      expect(result.current).toHaveProperty('loadSubDirectorySuggestions')
      expect(typeof result.current.handleUpdateReference).toBe('function')
      expect(typeof result.current.loadRootSuggestions).toBe('function')
      expect(typeof result.current.loadSubDirectorySuggestions).toBe('function')
    })
  })
})
