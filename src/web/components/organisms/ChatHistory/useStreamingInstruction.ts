import { useState, useMemo, useCallback } from 'react'

import { useStreamingFetch } from '@/hooks/useStreamingFetch'
import { API_BASE_URL } from '@/lib/api/client'
import { getSession, SessionDetail } from '@/lib/api/session/getSession'

type UseStreamingInstruction = {
  streamedText: string
  isStreaming: boolean
  streamingError: string | null // Use error directly from useStreamingFetch
  onSendInstruction: (instruction: string) => Promise<void>
  setStreamedText: (text: string) => void
  streamingTrigger: { instruction: string; sessionId: string } | null
  setStreamingTrigger: (
    trigger: { instruction: string; sessionId: string } | null,
  ) => void
}

export const useStreamingInstruction = (
  currentSessionId: string | null,
  setSessionDetail: (data: SessionDetail | null) => void,
): UseStreamingInstruction => {
  const [streamingTrigger, setStreamingTrigger] = useState<{
    instruction: string
    sessionId: string
  } | null>(null)
  // const [error, setError] = useState<string | null>(null) // Remove internal error state

  const memoizedStreamingOptions = useMemo((): RequestInit | undefined => {
    if (!streamingTrigger) return undefined

    return {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ instruction: streamingTrigger.instruction }),
    }
  }, [streamingTrigger])

  const {
    streamedText,
    isLoading: isStreaming,
    error: streamingError, // Get error directly from useStreamingFetch
    setStreamedText,
  } = useStreamingFetch(
    streamingTrigger
      ? `${API_BASE_URL}/session/${streamingTrigger.sessionId}/instruction`
      : null,
    memoizedStreamingOptions,
    {
      onComplete: (err, finalText) => {
        // Called when streaming finished (either successfully or with error).
        // We will load the session detail here so the hook owns the post-stream refresh.
        if (finalText.length > 0 || err) {
          void (async (): Promise<void> => {
            if (!currentSessionId) return
            try {
              const data = await getSession(currentSessionId)
              setSessionDetail(data.session)
            } catch (err: unknown) {
              // Caller (useSessionManagement) manages error state; just log here.
              console.error('Failed to load session data after streaming:', err)
            }
          })()
        }

        // Clear trigger and streamed text.
        setStreamingTrigger(null)
        setStreamedText('')
      },
    },
  )

  // Completion is handled by useStreamingFetch onComplete callback passed above.

  const onSendInstruction = useCallback(
    async (instruction: string): Promise<void> => {
      if (!currentSessionId) return
      console.log('Instruction to send:', instruction)
      setStreamingTrigger({ instruction, sessionId: currentSessionId })
    },
    [currentSessionId, setStreamingTrigger],
  )

  return {
    streamedText,
    isStreaming,
    streamingError, // Expose error directly from useStreamingFetch
    onSendInstruction,
    setStreamedText,
    streamingTrigger,
    setStreamingTrigger,
  }
}
