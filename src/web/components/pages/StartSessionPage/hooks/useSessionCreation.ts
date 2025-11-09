import { useCallback } from 'react'

import { useToast } from '@/components/organisms/Toast/hooks/useToast'
import type { StartSessionRequest } from '@/lib/api/session/startSession'
import { startSession } from '@/lib/api/session/startSession'

export const useSessionCreation = (): {
  handleSubmit: (data: StartSessionRequest) => Promise<void>
} => {
  const toast = useToast()

  const handleSubmit = useCallback(
    async (data: StartSessionRequest) => {
      try {
        const result = await startSession(data)
        if (result.session_id) {
          window.location.href = `/session/${result.session_id}`
        } else {
          toast.failure('Failed to create session: No session ID returned.')
        }
      } catch (error_: unknown) {
        toast.failure(
          (error_ as Error).message || 'An error occurred during session creation.',
        )
      }
    },
    [toast],
  )

  return { handleSubmit }
}
