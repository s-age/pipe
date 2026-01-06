import { useMemo } from 'react'

import type { Turn } from '@/lib/api/session/getSession'
import { segmentsToTurns } from '@/lib/turns/turnFactory'
import type { ChatSegment } from '@/types/chat'

/**
 * Extract tool name from tool call content
 * Matches patterns like "Tool call: google_web_search"
 */
const extractToolName = (content: string): string | undefined => {
  const match = content.match(/Tool call:\s*(\w+)/i)

  return match ? match[1] : undefined
}

/**
 * Check if content is a tool call (function invocation)
 */
const isToolCall = (content: string): boolean => /Tool call:/i.test(content)

/**
 * Detect tool status from content
 * Returns 'succeeded', 'failed', or undefined
 */
const detectToolStatus = (content: string): 'succeeded' | 'failed' | undefined => {
  if (/Tool status:\s*succeeded/i.test(content)) return 'succeeded'
  if (/Tool status:\s*failed/i.test(content)) return 'failed'

  return undefined
}

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
        const toolName = extractToolName(part)
        const toolStatus = detectToolStatus(part)
        const isCall = isToolCall(part)

        // Determine the status based on content
        let status: 'running' | 'completed' | 'succeeded' | 'failed' = 'running'

        if (isClosed) {
          // If it has an explicit status, use it
          if (toolStatus) {
            status = toolStatus
          }
          // If it's a tool call but no explicit status, mark as completed
          else if (isCall) {
            status = 'completed'
          }
          // Otherwise it's a completed block
          else {
            status = 'completed'
          }
        }

        return {
          type: 'tool',
          content: part,
          name: toolName,
          status,
          isComplete: !isStreaming || isClosed
        } as ChatSegment
      }

      // Text block - only return if it has meaningful content
      const trimmedContent = part.trim()
      if (!trimmedContent) return null

      return {
        type: 'text',
        content: part,
        isComplete: !isStreaming
      } as ChatSegment
    })
    .filter((segment): segment is ChatSegment => segment !== null)
}

type UseChatStreamParserProperties = {
  instructionTurn: Turn | null
  isStreaming: boolean
  streamedText: string
}

export const useChatStreamParser = ({
  instructionTurn,
  isStreaming,
  streamedText
}: UseChatStreamParserProperties): { streamingTurns: Turn[] } => {
  // Compute segments from accumulated text
  const segments = useMemo(
    () => parseContentToSegments(streamedText, isStreaming),
    [streamedText, isStreaming]
  )

  // Convert segments to Turn objects for display
  const streamingTurns = useMemo(() => {
    const segmentTurns = segmentsToTurns(segments)

    // Prepend instruction turn if it exists
    return instructionTurn ? [instructionTurn, ...segmentTurns] : segmentTurns
  }, [segments, instructionTurn])

  return { streamingTurns }
}
