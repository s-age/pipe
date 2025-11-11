import { useCallback } from 'react'

import { useToast } from '@/components/organisms/Toast/hooks/useToast'
import type { StartSessionRequest } from '@/lib/api/session/startSession'

import { useStartSessionPageActions } from './useStartSessionPageActions'

export const useStartSessionPageHandlers = (): {
  handleSubmit: (data: StartSessionRequest) => Promise<void>
} => {
  const toast = useToast()
  const { createSession } = useStartSessionPageActions()

  const handleSubmit = useCallback(
    async (data: StartSessionRequest): Promise<void> => {
      try {
        const result = await createSession(data)
        if (result.session_id) {
          window.location.href = `/session/${result.session_id}`
        } else {
          toast.failure('Failed to create session: No session ID returned.')
        }
      } catch (error_: unknown) {
        toast.failure(
          (error_ as Error).message || 'An error occurred during session creation.'
        )
      }
    },
    [createSession, toast]
  )

  return { handleSubmit }
}
