import { renderHook, waitFor } from '@testing-library/react'
import { setupServer } from 'msw/node'

import { doctorHandlers, doctorErrorHandlers } from '@/msw/resources/doctor'
import { therapistHandlers, therapistErrorHandlers } from '@/msw/resources/therapist'
import { clearToasts, getToasts } from '@/stores/useToastStore'

import { useTherapistActions } from '../useTherapistActions'

const server = setupServer(...therapistHandlers, ...doctorHandlers)

describe('useTherapistActions', () => {
  beforeAll(() => server.listen())
  afterEach(() => {
    server.resetHandlers()
    clearToasts()
  })
  afterAll(() => server.close())

  describe('hook structure', () => {
    it('should return all action functions', () => {
      const { result } = renderHook(() => useTherapistActions())

      expect(result.current).toHaveProperty('diagnoseSession')
      expect(result.current).toHaveProperty('applyModifications')
      expect(typeof result.current.diagnoseSession).toBe('function')
      expect(typeof result.current.applyModifications).toBe('function')
    })
  })

  describe('diagnoseSession', () => {
    it('should diagnose session successfully and show success toast', async () => {
      const { result } = renderHook(() => useTherapistActions())

      const diagnosis = await result.current.diagnoseSession('test-session-id')

      await waitFor(() => {
        const toasts = getToasts()
        expect(toasts).toHaveLength(1)
        expect(toasts[0].status).toBe('success')
        expect(toasts[0].title).toBe('Diagnosis completed successfully')
      })

      expect(diagnosis).toEqual({
        summary:
          'The session contains some redundant turns and could be improved by editing turn 2.',
        deletions: [1],
        edits: [{ turn: 2, newContent: 'Improved content for turn 2' }],
        compressions: [{ start: 1, end: 2, reason: 'Redundant interaction' }],
        rawDiagnosis: 'Raw diagnosis data for debugging'
      })
    })

    it('should handle diagnosis error and show failure toast', async () => {
      server.use(...therapistErrorHandlers)
      const { result } = renderHook(() => useTherapistActions())

      const diagnosis = await result.current.diagnoseSession('test-session-id')

      await waitFor(() => {
        const toasts = getToasts()
        expect(toasts).toHaveLength(1)
        expect(toasts[0].status).toBe('failure')
        expect(toasts[0].title).toBe('Diagnosis failed')
        expect(toasts[0].description).toBe('Diagnosis failed')
      })

      expect(diagnosis).toBeUndefined()
    })
  })

  describe('applyModifications', () => {
    const modifications = {
      deletions: [1],
      edits: [{ turn: 2, newContent: 'Updated' }]
    }

    it('should apply modifications successfully and show success toast', async () => {
      const { result } = renderHook(() => useTherapistActions())

      await result.current.applyModifications('test-session-id', modifications)

      await waitFor(() => {
        const toasts = getToasts()
        expect(toasts).toHaveLength(1)
        expect(toasts[0].status).toBe('success')
        expect(toasts[0].title).toBe('Modifications applied successfully')
      })
    })

    it('should handle failed status from API and show failure toast', async () => {
      // Use the second handler in doctorErrorHandlers which returns status: 'Failed'
      server.use(doctorErrorHandlers[1])
      const { result } = renderHook(() => useTherapistActions())

      await result.current.applyModifications('test-session-id', modifications)

      await waitFor(() => {
        const toasts = getToasts()
        expect(toasts).toHaveLength(1)
        expect(toasts[0].status).toBe('failure')
        expect(toasts[0].title).toBe('Failed to apply modifications')
        expect(toasts[0].description).toBe('Validation error')
      })
    })

    it('should handle API error and show failure toast', async () => {
      // Use the first handler in doctorErrorHandlers which returns 500
      server.use(doctorErrorHandlers[0])
      const { result } = renderHook(() => useTherapistActions())

      await result.current.applyModifications('test-session-id', modifications)

      await waitFor(() => {
        const toasts = getToasts()
        expect(toasts).toHaveLength(1)
        expect(toasts[0].status).toBe('failure')
        expect(toasts[0].title).toBe('Failed to apply modifications')
        expect(toasts[0].description).toBe('Failed to apply modifications')
      })
    })
  })
})
