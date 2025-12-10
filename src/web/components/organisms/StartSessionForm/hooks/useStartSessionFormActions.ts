import { useCallback } from 'react'

import { startSession } from '@/lib/api/session/startSession'
import { addToast } from '@/stores/useToastStore'

import type { StartSessionFormInputs } from '../schema'

export type UseStartSessionFormActionsReturn = {
  startSessionAction: (data: StartSessionFormInputs) => Promise<{ sessionId: string }>
}

export const useStartSessionFormActions = (): UseStartSessionFormActionsReturn => {
  const startSessionAction = useCallback(
    async (data: StartSessionFormInputs): Promise<{ sessionId: string }> => {
      try {
        const result = await startSession(data)
        if (result.sessionId) {
          addToast({ status: 'success', title: 'Session created successfully' })

          return result
        } else {
          addToast({
            status: 'failure',
            title: 'Failed to create session: No session ID returned.'
          })
          throw new Error('Failed to create session: No session ID returned.')
        }
      } catch (error: unknown) {
        addToast({
          status: 'failure',
          title:
            (error as Error).message || 'An error occurred during session creation.'
        })
        throw error
      }
    },
    []
  )

  return { startSessionAction }
}
