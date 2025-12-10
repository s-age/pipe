import { useCallback } from 'react'

import type { StartSessionRequest } from '@/lib/api/session/startSession'

import { useStartSessionPageActions } from './useStartSessionPageActions'

export const useStartSessionPageHandlers = (): {
  handleSubmit: (data: StartSessionRequest) => Promise<void>
} => {
  const { createSession } = useStartSessionPageActions()

  const handleSubmit = useCallback(
    async (data: StartSessionRequest): Promise<void> => {
      const result = await createSession(data)
      if (result.sessionId) {
        window.location.href = `/session/${result.sessionId}`
      }
    },
    [createSession]
  )

  return { handleSubmit }
}
