import { useCallback } from 'react'

import type { StartSessionRequest } from '@/lib/api/session/startSession'
import { startSession } from '@/lib/api/session/startSession'
import { addToast } from '@/stores/useToastStore'

export const useStartSessionPageActions = (): {
  createSession: (data: StartSessionRequest) => Promise<{ sessionId: string } | void>
} => {
  const createSession = useCallback(
    async (data: StartSessionRequest): Promise<{ sessionId: string } | void> => {
      try {
        const result = await startSession(data)

        addToast({
          status: 'success',
          title: 'Session created successfully'
        })

        return result
      } catch (error: unknown) {
        addToast({
          status: 'failure',
          title: (error as Error).message || 'Failed to create session'
        })
      }
    },
    []
  )

  return { createSession }
}
