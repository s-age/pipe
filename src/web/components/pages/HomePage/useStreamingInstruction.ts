import { useState, useMemo, useCallback } from 'react'

import { useStreamingFetch } from '@/hooks/useStreamingFetch'
import { API_BASE_URL } from '@/lib/api/client'

type UseStreamingInstruction = {
  streamedText: string
  isStreaming: boolean
  streamingError: string | null // Use error directly from useStreamingFetch
  handleSendInstruction: (instruction: string) => Promise<void>
  setStreamedText: (text: string) => void
  streamingTrigger: { instruction: string; sessionId: string } | null
  setStreamingTrigger: (
    trigger: { instruction: string; sessionId: string } | null,
  ) => void
}

export const useStreamingInstruction = (
  currentSessionId: string | null,
  loadSessionDetailAfterStreaming: () => Promise<void>,
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
        // Do not set component state synchronously inside an effect here — this callback
        // is invoked from the streaming hook after the fetch loop completes.
        // We can safely call loadSessionDetailAfterStreaming and then clear trigger/text.
        if (finalText.length > 0 || err) {
          // Fire-and-forget; the caller handles errors internally if needed
          void loadSessionDetailAfterStreaming()
        }

        // Clear trigger and streamed text. These are safe to call here because this
        // callback is invoked after the streaming lifecycle finishes inside the hook.
        setStreamingTrigger(null)
        setStreamedText('')
      },
    },
  )

  // Completion is handled by useStreamingFetch onComplete callback passed above.

  const handleSendInstruction = useCallback(
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
    handleSendInstruction,
    setStreamedText,
    streamingTrigger,
    setStreamingTrigger,
  }
}
