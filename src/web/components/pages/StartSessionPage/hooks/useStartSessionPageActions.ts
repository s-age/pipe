import { useCallback } from 'react'

import type { StartSessionRequest } from '@/lib/api/session/startSession'
import { startSession } from '@/lib/api/session/startSession'

export const useStartSessionPageActions = (): {
  createSession: (data: StartSessionRequest) => Promise<{ session_id: string }>
} => {
  const createSession = useCallback(
    async (data: StartSessionRequest): Promise<{ session_id: string }> =>
      await startSession(data),
    []
  )

  return { createSession }
}
