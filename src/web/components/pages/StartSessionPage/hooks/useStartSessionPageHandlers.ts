import { useCallback } from 'react'

import type { StartSessionRequest } from '@/lib/api/session/startSession'
import { emitToast } from '@/lib/toastEvents'

import { useStartSessionPageActions } from './useStartSessionPageActions'

export const useStartSessionPageHandlers = (): {
  handleSubmit: (data: StartSessionRequest) => Promise<void>
} => {
  const { createSession } = useStartSessionPageActions()

  const handleSubmit = useCallback(
    async (data: StartSessionRequest): Promise<void> => {
      try {
        const result = await createSession(data)
        if (result.session_id) {
          window.location.href = `/session/${result.session_id}`
        } else {
          emitToast.failure('Failed to create session: No session ID returned.')
        }
      } catch (error_: unknown) {
        emitToast.failure(
          (error_ as Error).message || 'An error occurred during session creation.'
        )
      }
    },
    [createSession]
  )

  return { handleSubmit }
}
