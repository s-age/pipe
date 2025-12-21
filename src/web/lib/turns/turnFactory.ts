import type {
  Turn,
  UserTaskTurn,
  ModelResponseTurn,
  FunctionCallingTurn,
  ToolResponseTurn
} from '@/lib/api/session/getSession'
import type { ChatSegment } from '@/types/chat'

/**
 * Create a UserTaskTurn from an instruction
 */
export const createUserTaskTurn = (
  instruction: string,
  timestamp: string
): UserTaskTurn => ({
  type: 'user_task',
  instruction,
  timestamp
})

/**
 * Create a ModelResponseTurn from a text segment
 */
export const createModelResponseTurn = (
  content: string,
  timestamp: string
): ModelResponseTurn => ({
  type: 'model_response',
  content,
  timestamp
})

/**
 * Create a FunctionCallingTurn from a tool segment
 */
export const createFunctionCallingTurn = (
  response: string,
  timestamp: string
): FunctionCallingTurn => ({
  type: 'function_calling',
  response,
  timestamp
})

/**
 * Detect if content is a Tool status response
 * Returns the status (e.g., 'succeeded', 'failed') if it matches, otherwise null
 */
export const extractToolStatus = (content: string): string | null => {
  // Match patterns like "Tool status: succeeded" or "Tool status: failed"
  const match = content.match(/Tool status:\s*(\w+)/i)

  return match ? match[1].toLowerCase() : null
}

/**
 * Create a ToolResponseTurn from tool response data
 */
export const createToolResponseTurn = (
  name: string,
  status: string,
  message: string,
  timestamp: string
): ToolResponseTurn => ({
  type: 'tool_response',
  name,
  response: {
    status,
    message
  },
  timestamp
})

/**
 * Create a tool response turn from a tool status chunk
 * Extracts tool name and status from content like "Tool status: succeeded"
 */
export const createToolResponseTurnFromChunk = (
  content: string,
  toolName: string = 'unknown',
  timestamp: string
): ToolResponseTurn | null => {
  const status = extractToolStatus(content)
  if (!status) return null

  return createToolResponseTurn(toolName, status, content.trim(), timestamp)
}

/**
 * Dispatcher function to convert a ChatSegment to the appropriate Turn type
 * Returns the correct Turn based on segment type and status
 */
export const segmentToTurn = (segment: ChatSegment): Turn => {
  const timestamp = new Date().toISOString()

  switch (segment.type) {
    case 'tool': {
      // Check if this is a tool response (succeeded/failed)
      if (segment.status === 'succeeded' || segment.status === 'failed') {
        const toolResponseTurn = createToolResponseTurnFromChunk(
          segment.content,
          segment.name || 'unknown',
          timestamp
        )

        return toolResponseTurn || createFunctionCallingTurn(segment.content, timestamp)
      }

      // Otherwise treat as function calling (tool invocation/call)
      return createFunctionCallingTurn(segment.content, timestamp)
    }

    case 'text':
      return createModelResponseTurn(segment.content, timestamp)
  }
}

/**
 * Convert an array of ChatSegments to Turn objects
 */
export const segmentsToTurns = (segments: ChatSegment[]): Turn[] =>
  segments.map(segmentToTurn)
