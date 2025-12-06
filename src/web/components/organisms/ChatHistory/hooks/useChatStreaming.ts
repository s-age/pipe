import { useState, useEffect, useRef, useCallback, type RefObject } from 'react'

import type { SessionDetail } from '@/lib/api/session/getSession'
import { getSession } from '@/lib/api/session/getSession'
import { streamInstruction } from '@/lib/api/session/streamInstruction'
import { addToast } from '@/stores/useToastStore'

type SessionDetailCache = {
  [sessionId: string]: {
    detail: SessionDetail
    timestamp: number
  }
}

const SESSION_DETAIL_CACHE_TTL = 30000 // 30秒

type ChatStreamingProperties = {
  currentSessionId: string | null
  setSessionDetail: (data: SessionDetail | null) => void
}

type ChatStreamingReturn = {
  streamedText: string | null
  isStreaming: boolean
  turnsListReference: RefObject<HTMLDivElement | null>
  scrollToBottom: () => void
  onSendInstruction: (instruction: string) => Promise<void>
}

export const useChatStreaming = ({
  currentSessionId,
  setSessionDetail
}: ChatStreamingProperties): ChatStreamingReturn => {
  const [streamingTrigger, setStreamingTrigger] = useState<{
    instruction: string
    sessionId: string
  } | null>(null)
  const [streamedText, setStreamedText] = useState<string>('')
  const [isLoading, setIsLoading] = useState<boolean>(false)
  const [error, setError] = useState<string | null>(null)
  const controllerReference = useRef<AbortController | null>(null)
  const sessionDetailCacheReference = useRef<SessionDetailCache>({})
  const turnsListReference = useRef<HTMLDivElement | null>(null)

  // Session detail cache helpers
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

  // Streaming fetch effect (merged from useStreamingFetch)
  useEffect((): (() => void) => {
    if (!streamingTrigger) {
      setStreamedText('')
      if (controllerReference.current) {
        controllerReference.current.abort()
      }

      return (): void => {}
    }

    // Cleanup old controller before starting new request
    if (controllerReference.current) {
      controllerReference.current.abort()
    }
    controllerReference.current = new AbortController()
    const signal = controllerReference.current.signal

    const fetchData = async (): Promise<void> => {
      setIsLoading(true)
      setError(null)
      setStreamedText('')
      let localError: string | null = null
      let accum = ''

      try {
        const stream = await streamInstruction(streamingTrigger.sessionId, {
          instruction: streamingTrigger.instruction,
          signal
        })

        const reader = stream.getReader()
        const decoder = new TextDecoder()
        let done = false

        while (!done) {
          const { value, done: readerDone } = await reader.read()
          done = readerDone
          const chunk = decoder.decode(value, { stream: true })

          if (chunk) {
            accum += chunk
            setStreamedText((previous) => previous + chunk)
          }
        }
      } catch (error_: unknown) {
        localError = (error_ as Error).message || 'Failed to fetch stream.'
        setError(localError)
      } finally {
        setIsLoading(false)

        // Handle completion (merged from useStreamingInstruction)
        if (accum.length > 0 || localError) {
          void (async (): Promise<void> => {
            if (!currentSessionId) {
              return
            }

            // Try to get from cache
            const cachedDetail = getSessionDetailFromCache(currentSessionId)
            if (cachedDetail) {
              setSessionDetail(cachedDetail)

              return
            }

            // Fetch from API if not cached
            try {
              const data = await getSession(currentSessionId)
              cacheSessionDetail(currentSessionId, data.session)
              setSessionDetail(data.session)
            } catch {
              addToast({
                status: 'failure',
                title: 'Failed to load session data after streaming.'
              })
            }
          })()
        }

        // Clear trigger and streamed text
        setStreamingTrigger(null)
        setStreamedText('')
      }
    }

    void fetchData()

    return (): void => {
      if (controllerReference.current) {
        controllerReference.current.abort()
      }
    }
  }, [
    streamingTrigger,
    currentSessionId,
    setSessionDetail,
    getSessionDetailFromCache,
    cacheSessionDetail
  ])

  // Propagate streaming errors
  useEffect(() => {
    if (error) {
      const message = typeof error === 'string' ? error : (error as Error).message
      addToast({ status: 'failure', title: message })
      setStreamingTrigger(null)
    }
  }, [error])

  // Scroll management
  const scrollToBottom = useCallback((): void => {
    if (turnsListReference.current) {
      turnsListReference.current.scrollTop = turnsListReference.current.scrollHeight
    }
  }, [])

  // Auto-scroll when streaming text appears or when session changes
  useEffect(() => {
    scrollToBottom()
  }, [streamedText, currentSessionId, scrollToBottom])

  // Send instruction handler
  const onSendInstruction = useCallback(
    async (instruction: string): Promise<void> => {
      if (!currentSessionId) return
      setStreamingTrigger({ instruction, sessionId: currentSessionId })
    },
    [currentSessionId]
  )

  return {
    streamedText: streamedText || null,
    isStreaming: isLoading,
    turnsListReference,
    scrollToBottom,
    onSendInstruction
  }
}

export type { ChatStreamingReturn, ChatStreamingProperties }
