import { useCallback } from 'react'

import { startSession } from '@/lib/api/session/startSession'
import { emitToast } from '@/lib/toastEvents'

import type { StartSessionFormInputs } from '../schema'

export type UseStartSessionFormActionsReturn = {
  startSessionAction: (data: StartSessionFormInputs) => Promise<{ session_id: string }>
}

export const useStartSessionFormActions = (): UseStartSessionFormActionsReturn => {
  const startSessionAction = useCallback(
    async (data: StartSessionFormInputs): Promise<{ session_id: string }> => {
      try {
        const result = await startSession(data)
        if (result.session_id) {
          emitToast.success('Session created successfully')

          return result
        } else {
          emitToast.failure('Failed to create session: No session ID returned.')
          throw new Error('Failed to create session: No session ID returned.')
        }
      } catch (error: unknown) {
        emitToast.failure(
          (error as Error).message || 'An error occurred during session creation.'
        )
        throw error
      }
    },
    []
  )

  return { startSessionAction }
}
