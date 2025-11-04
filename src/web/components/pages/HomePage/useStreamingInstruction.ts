import { useState, useEffect, useMemo, useCallback } from 'react'
import { useStreamingFetch } from '@/hooks/useStreamingFetch'
import { API_BASE_URL } from '@/lib/api/client'
import { SessionData } from '@/lib/api/session/getSession'

interface UseStreamingInstruction {
  streamedText: string
  isStreaming: boolean
  streamingError: string | null
  handleSendInstruction: (instruction: string) => Promise<void>
  setStreamedText: (text: string) => void
  streamingTrigger: { instruction: string; sessionId: string } | null
  setStreamingTrigger: (trigger: { instruction: string; sessionId: string } | null) => void
}

export const useStreamingInstruction = (
  currentSessionId: string | null,
  setSessionData: (data: SessionData | null) => void,
  loadSessionDataAfterStreaming: () => Promise<void>,
): UseStreamingInstruction => {
  const [streamingTrigger, setStreamingTrigger] = useState<{ instruction: string; sessionId: string } | null>(null)
  const [error, setError] = useState<string | null>(null) // エラー状態を内部で管理

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
    error: streamingError,
    setStreamedText,
  } = useStreamingFetch(
    streamingTrigger
      ? `${API_BASE_URL}/session/${streamingTrigger.sessionId}/instruction`
      : null,
    memoizedStreamingOptions,
  )

  useEffect(() => {
    if (streamingError) {
      setError(streamingError)
      setStreamingTrigger(null)
    }
  }, [streamingError])

  useEffect(() => {
    if (streamingTrigger && !isStreaming) {
      if (streamedText.length > 0 || streamingError) {
        loadSessionDataAfterStreaming()
        setStreamingTrigger(null)
        setStreamedText('')
      }
    }
  }, [isStreaming, streamingTrigger, streamedText, streamingError, setStreamedText, loadSessionDataAfterStreaming])

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
    streamingError: error, // 内部のエラー状態を公開
    handleSendInstruction,
    setStreamedText,
    streamingTrigger,
    setStreamingTrigger,
  }
}
