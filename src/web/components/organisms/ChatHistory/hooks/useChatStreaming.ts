import { useEffect, useRef, useCallback, type RefObject } from 'react'

import { useChatStreamParser } from '@/hooks/useChatStreamParser'
import { useStreamingClient } from '@/hooks/useStreamingClient'
import type { SessionDetail } from '@/lib/api/session/getSession'
import type { Turn } from '@/lib/api/session/getSession'
import { getSession } from '@/lib/api/session/getSession'
import { addToast } from '@/stores/useToastStore'

type SessionDetailCache = {
  [sessionId: string]: {
    detail: SessionDetail
    timestamp: number
  }
}

const SESSION_DETAIL_CACHE_TTL = 30000 // 30 seconds

type ChatStreamingProperties = {
  currentSessionId: string | null
  setSessionDetail: (data: SessionDetail | null) => void
}

type ChatStreamingReturn = {
  streamingTurns: Turn[]
  isStreaming: boolean
  turnsListReference: RefObject<HTMLDivElement | null>
  scrollToBottom: () => void
  onSendInstruction: (instruction: string) => Promise<void>
}

export const useChatStreaming = ({
  currentSessionId,
  setSessionDetail
}: ChatStreamingProperties): ChatStreamingReturn => {
  const turnsListReference = useRef<HTMLDivElement | null>(null)
  const sessionDetailCacheReference = useRef<SessionDetailCache>({})
  const previousLoadingState = useRef<boolean>(false)

  // 1. Client Hook: Handles API communication and SSE state
  const { streamedText, isLoading, error, instructionTurn, startStreaming } =
    useStreamingClient()

  // 2. Parser Hook: Converts raw text to Turn objects
  const { streamingTurns } = useChatStreamParser({
    streamedText,
    isStreaming: isLoading,
    instructionTurn
  })

  // Session cache helpers
  const getSessionDetailFromCache = useCallback(
    (sessionId: string): SessionDetail | null => {
      const cached = sessionDetailCacheReference.current[sessionId]
      if (!cached) return null

      const now = Date.now()
      if (now - cached.timestamp > SESSION_DETAIL_CACHE_TTL) {
        delete sessionDetailCacheReference.current[sessionId]

        return null
      }

      return cached.detail
    },
    []
  )

  const cacheSessionDetail = useCallback(
    (sessionId: string, detail: SessionDetail): void => {
      sessionDetailCacheReference.current[sessionId] = {
        detail,
        timestamp: Date.now()
      }
    },
    []
  )

  // 3. Error Handling
  useEffect(() => {
    if (error) {
      addToast({ status: 'failure', title: error })
    }
  }, [error])

  // 4. Session Refresh on Completion
  // Detect when loading finishes (true -> false) to refresh session data
  useEffect(() => {
    const wasLoading = previousLoadingState.current
    if (wasLoading && !isLoading) {
      // Streaming finished
      if (streamedText.length > 0 && currentSessionId) {
        void (async (): Promise<void> => {
          // Try to get from cache first
          const cachedDetail = getSessionDetailFromCache(currentSessionId)
          if (cachedDetail) {
            setSessionDetail(cachedDetail)

            return
          }

          // Fetch from API
          try {
            const data = await getSession(currentSessionId)
            cacheSessionDetail(currentSessionId, data)
            setSessionDetail(data)
          } catch {
            addToast({
              status: 'failure',
              title: 'Failed to load session data after streaming.'
            })
          }
        })()
      }
    }
    previousLoadingState.current = isLoading
  }, [
    isLoading,
    streamedText,
    currentSessionId,
    setSessionDetail,
    getSessionDetailFromCache,
    cacheSessionDetail
  ])

  // 5. Scroll Management
  const scrollToBottom = useCallback((): void => {
    if (turnsListReference.current) {
      turnsListReference.current.scrollTop = turnsListReference.current.scrollHeight
    }
  }, [])

  // Auto-scroll when new content arrives
  useEffect(() => {
    scrollToBottom()
  }, [streamingTurns, scrollToBottom, currentSessionId])

  // 6. Action Handler
  const onSendInstruction = useCallback(
    async (instruction: string): Promise<void> => {
      if (!currentSessionId) return
      await startStreaming(currentSessionId, instruction)
    },
    [currentSessionId, startStreaming]
  )

  return {
    streamingTurns,
    isStreaming: isLoading,
    turnsListReference,
    scrollToBottom,
    onSendInstruction
  }
}

export type { ChatStreamingReturn, ChatStreamingProperties }
