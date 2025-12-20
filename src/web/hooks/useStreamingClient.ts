import { useState, useRef, useEffect, useCallback } from 'react'

import type { Turn } from '@/lib/api/session/getSession'
import { streamInstruction } from '@/lib/api/session/streamInstruction'
import { createUserTaskTurn } from '@/lib/turns/turnFactory'
import type { SSEEvent } from '@/types/chat'

type UseStreamingClientReturn = {
  streamedText: string
  isLoading: boolean
  error: string | null
  instructionTurn: Turn | null
  startStreaming: (sessionId: string, instruction: string) => Promise<void>
  abortStreaming: () => void
  reset: () => void
}

export const useStreamingClient = (): UseStreamingClientReturn => {
  const [streamedText, setStreamedText] = useState<string>('')
  const [isLoading, setIsLoading] = useState<boolean>(false)
  const [error, setError] = useState<string | null>(null)
  const [instructionTurn, setInstructionTurn] = useState<Turn | null>(null)

  const controllerReference = useRef<AbortController | null>(null)

  const abortStreaming = useCallback(() => {
    if (controllerReference.current) {
      controllerReference.current.abort()
      controllerReference.current = null
    }
    setIsLoading(false)
  }, [])

  const reset = useCallback(() => {
    setStreamedText('')
    setError(null)
    setInstructionTurn(null)
    abortStreaming()
  }, [abortStreaming])

  const startStreaming = useCallback(async (sessionId: string, instruction: string) => {
    // Reset states for new stream
    setStreamedText('')
    setError(null)
    setInstructionTurn(null)

    // Cleanup previous controller
    if (controllerReference.current) {
      controllerReference.current.abort()
    }
    controllerReference.current = new AbortController()
    const signal = controllerReference.current.signal

    setIsLoading(true)
    let accumContent = ''

    try {
      const stream = await streamInstruction(sessionId, {
        instruction,
        signal
      })

      const reader = stream.getReader()
      const decoder = new TextDecoder()
      let done = false
      let buffer = ''

      while (!done) {
        const { value, done: readerDone } = await reader.read()
        done = readerDone
        const chunk = decoder.decode(value, { stream: true })

        if (chunk) {
          buffer += chunk
          const lines = buffer.split('\n')
          buffer = lines.pop() || ''

          for (const line of lines) {
            const trimmed = line.trim()
            if (!trimmed.startsWith('data: ')) continue

            const jsonString = trimmed.replace('data: ', '').trim()
            if (jsonString === '[DONE]') continue

            try {
              const data = JSON.parse(jsonString) as SSEEvent

              if (data.type === 'instruction' && data.content) {
                setInstructionTurn(
                  createUserTaskTurn(data.content, new Date().toISOString())
                )
              }

              if (data.type === 'chunk' && data.content) {
                accumContent += data.content
                setStreamedText(accumContent)
              }

              if (data.type === 'complete') {
                done = true
                break
              }
            } catch {
              // Parse error within stream is considered minor, usually ignored or logged
              // We could set a warning, but for now we continue
              // eslint-disable-next-line no-console
              console.warn('Failed to parse SSE data chunk')
            }
          }
        }
      }
    } catch (error_: unknown) {
      if ((error_ as Error).name === 'AbortError') {
        // Ignore abort errors
        return
      }
      setError((error_ as Error).message || 'Failed to fetch stream.')
    } finally {
      setIsLoading(false)
      controllerReference.current = null
    }
  }, [])

  // Cleanup on unmount
  useEffect(
    (): (() => void) => (): void => {
      if (controllerReference.current) {
        controllerReference.current.abort()
      }
    },
    []
  )

  return {
    streamedText,
    isLoading,
    error,
    instructionTurn,
    startStreaming,
    abortStreaming,
    reset
  }
}
