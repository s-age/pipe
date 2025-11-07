import { useState, useCallback } from 'react'

import { startSession, StartSessionRequest } from '@/lib/api/session/startSession'

type UseSessionCreationResult = {
  handleSubmit: (data: StartSessionRequest) => Promise<void>
  error: string | null
}

export const useSessionCreation = (): UseSessionCreationResult => {
  const [error, setError] = useState<string | null>(null)

  const handleSubmit = useCallback(async (data: StartSessionRequest) => {
    setError(null)
    try {
      const result = await startSession(data)
      if (result.session_id) {
        window.location.href = `/session/${result.session_id}`
      } else {
        setError('Failed to create session: No session ID returned.')
      }
    } catch (err: unknown) {
      setError((err as Error).message || 'An error occurred during session creation.')
    }
  }, [])

  return { handleSubmit, error }
}
