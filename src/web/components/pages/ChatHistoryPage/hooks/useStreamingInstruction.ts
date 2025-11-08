import { useState, useMemo, useCallback, useRef } from 'react'

import { useStreamingFetch } from '@/components/pages/ChatHistoryPage/hooks/useStreamingFetch'
import { API_BASE_URL } from '@/lib/api/client'
import type { SessionDetail } from '@/lib/api/session/getSession'
import { getSession } from '@/lib/api/session/getSession'

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

type SessionDetailCache = {
  [sessionId: string]: {
    detail: SessionDetail
    timestamp: number
  }
}

const SESSION_DETAIL_CACHE_TTL = 30000 // 30秒

export const useStreamingInstruction = (
  currentSessionId: string | null,
  setSessionDetail: (data: SessionDetail | null) => void,
): UseStreamingInstruction => {
  const [streamingTrigger, setStreamingTrigger] = useState<{
    instruction: string
    sessionId: string
  } | null>(null)
  // const [error, setError] = useState<string | null>(null) // Remove internal error state

  // セッション詳細のキャッシュ（useRef を使用して再レンダー時の初期化を防ぐ）
  const sessionDetailCacheReference = useRef<SessionDetailCache>({})

  const getSessionDetailFromCache = useCallback(
    (sessionId: string): SessionDetail | null => {
      const cached = sessionDetailCacheReference.current[sessionId]
      if (!cached) {
        return null
      }

      const now = Date.now()
      if (now - cached.timestamp > SESSION_DETAIL_CACHE_TTL) {
        delete sessionDetailCacheReference.current[sessionId]

        return null
      }

      return cached.detail
    },
    [],
  )

  const cacheSessionDetail = useCallback(
    (sessionId: string, detail: SessionDetail): void => {
      sessionDetailCacheReference.current[sessionId] = {
        detail,
        timestamp: Date.now(),
      }
    },
    [],
  )

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
      onComplete: (error, finalText) => {
        // Called when streaming finished (either successfully or with error).
        // We will load the session detail here so the hook owns the post-stream refresh.
        if (finalText.length > 0 || error) {
          void (async (): Promise<void> => {
            if (!currentSessionId) {
              return
            }

            // キャッシュから取得を試みる
            const cachedDetail = getSessionDetailFromCache(currentSessionId)
            if (cachedDetail) {
              setSessionDetail(cachedDetail)

              return
            }

            // キャッシュにない場合は API から取得
            try {
              const data = await getSession(currentSessionId)
              cacheSessionDetail(currentSessionId, data.session)
              setSessionDetail(data.session)
            } catch (error: unknown) {
              // Caller (useSessionManagement) manages error state; just log here.
              console.error('Failed to load session data after streaming:', error)
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
