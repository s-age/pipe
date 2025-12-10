import {
  useState,
  useEffect,
  useRef,
  useCallback,
  useMemo,
  type RefObject
} from 'react'

import type { SessionDetail } from '@/lib/api/session/getSession'
import type { Turn } from '@/lib/api/session/getSession'
import { getSession } from '@/lib/api/session/getSession'
import { streamInstruction } from '@/lib/api/session/streamInstruction'
import { addToast } from '@/stores/useToastStore'
import type { ChatSegment, SSEEvent } from '@/types/chat'

type SessionDetailCache = {
  [sessionId: string]: {
    detail: SessionDetail
    timestamp: number
  }
}

const SESSION_DETAIL_CACHE_TTL = 30000 // 30秒

/**
 * Parse accumulated content into structured segments
 * Splits text by code blocks (```) to separate tool calls from regular text
 */
const parseContentToSegments = (
  fullText: string,
  isStreaming: boolean
): ChatSegment[] => {
  if (!fullText) return []

  // Split by code blocks, keeping the delimiters
  const parts = fullText.split(/(```[\s\S]*?```|```[\s\S]*$)/g)

  return parts
    .map((part) => {
      if (!part) return null

      // Tool block (starts with ``` and may or may not end with ```)
      if (part.startsWith('```')) {
        const isClosed = part.endsWith('```') && part.length > 3

        return {
          type: 'tool',
          content: part,
          status: isClosed ? 'completed' : 'running',
          isComplete: !isStreaming || isClosed
        } as ChatSegment
      }

      // Text block
      return {
        type: 'text',
        content: part,
        isComplete: !isStreaming
      } as ChatSegment
    })
    .filter((segment): segment is ChatSegment => segment !== null)
}

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

  // Compute segments from accumulated text
  const segments = useMemo(
    () => parseContentToSegments(streamedText, isLoading),
    [streamedText, isLoading]
  )

  // Convert segments to Turn objects for display
  const streamingTurns = useMemo(
    () =>
      segments.map(
        (segment): Turn => ({
          type: segment.type === 'tool' ? 'function_calling' : 'model_response',
          content: segment.content,
          timestamp: new Date().toISOString()
        })
      ),
    [segments]
  )

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
      let accumContent = '' // Accumulated content from chunks

      try {
        const stream = await streamInstruction(streamingTrigger.sessionId, {
          instruction: streamingTrigger.instruction,
          signal
        })

        const reader = stream.getReader()
        const decoder = new TextDecoder()
        let done = false
        let buffer = '' // Buffer for incomplete SSE lines

        while (!done) {
          const { value, done: readerDone } = await reader.read()
          done = readerDone
          const chunk = decoder.decode(value, { stream: true })

          if (chunk) {
            buffer += chunk

            // Process complete lines (SSE format: "data: {...}\n")
            const lines = buffer.split('\n')
            // Keep last incomplete line in buffer
            buffer = lines.pop() || ''

            for (const line of lines) {
              const trimmed = line.trim()
              if (!trimmed.startsWith('data: ')) continue

              const jsonString = trimmed.replace('data: ', '').trim()
              if (jsonString === '[DONE]') continue

              try {
                const data = JSON.parse(jsonString) as SSEEvent

                // Extract content from chunk events
                if (data.type === 'chunk' && data.content) {
                  accumContent += data.content
                  setStreamedText(accumContent)
                }
                // Handle other event types if needed
                // (start, instruction, complete events don't need to be displayed)
              } catch {
                addToast({
                  status: 'failure',
                  title: 'Failed to parse streaming data.'
                })
              }
            }
          }
        }
      } catch (error_: unknown) {
        localError = (error_ as Error).message || 'Failed to fetch stream.'
        setError(localError)
      } finally {
        setIsLoading(false)

        // Handle completion (merged from useStreamingInstruction)
        if (accumContent.length > 0 || localError) {
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
  }, [streamingTurns, currentSessionId, scrollToBottom])

  // Send instruction handler
  const onSendInstruction = useCallback(
    async (instruction: string): Promise<void> => {
      if (!currentSessionId) return
      setStreamingTrigger({ instruction, sessionId: currentSessionId })
    },
    [currentSessionId]
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
