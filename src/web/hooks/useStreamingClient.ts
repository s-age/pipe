import { useState, useRef, useEffect, useCallback } from 'react'

import type { Turn } from '@/lib/api/session/getSession'
import { streamInstruction } from '@/lib/api/session/streamInstruction'
import { createUserTaskTurn } from '@/lib/turns/turnFactory'
import type { SSEEvent } from '@/types/chat'

/**
 * useStreamingClient hook
 *
 * Handles streaming responses from both Gemini API and gemini-cli backends.
 * Converts different event formats into a unified text stream format that
 * can be parsed by useChatStreamParser.
 *
 * Supported formats:
 * - Gemini API: start, instruction, chunk, complete, error
 * - gemini-cli: init, message, tool_use, tool_result
 */

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

              // Handle Gemini API format (existing)
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

              // Handle gemini-cli format (new)
              // 'init' event starts a new session
              if (data.type === 'init') {
                // Session initialized, we can track session_id if needed
                // Currently just continue
              }

              // 'message' event contains the actual content
              if (data.type === 'message' && data.content) {
                // Parse the JSON content from the message
                try {
                  const messageContent = JSON.parse(data.content)

                  // Extract instruction if present
                  if (messageContent.current_task?.instruction) {
                    setInstructionTurn(
                      createUserTaskTurn(
                        messageContent.current_task.instruction,
                        data.timestamp
                      )
                    )
                  }
                } catch {
                  // If content is not JSON, treat it as plain text
                  accumContent += data.content
                  setStreamedText(accumContent)
                }
              }

              // 'tool_use' event indicates a tool is being called
              if (data.type === 'tool_use') {
                const toolCall = `\`\`\`\nTool call: ${data.tool_name}\nParameters: ${JSON.stringify(data.parameters, null, 2)}\n\`\`\``
                accumContent += toolCall + '\n\n'
                setStreamedText(accumContent)
              }

              // 'tool_result' event contains the tool execution result
              if (data.type === 'tool_result') {
                const toolResult = `\`\`\`\nTool status: ${data.status}\n${data.output || data.message || ''}\n\`\`\``
                accumContent += toolResult + '\n\n'
                setStreamedText(accumContent)
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
