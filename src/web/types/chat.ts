/* eslint-disable no-snake-case-properties/no-snake-case-properties */
/**
 * Chat segment types for streaming display
 */

export type ChatSegment =
  | { content: string; isComplete: boolean; type: 'text' }
  | {
      content: string
      isComplete: boolean
      type: 'tool'
      name?: string
      status?: 'running' | 'completed' | 'succeeded' | 'failed'
    }

/**
 * SSE event types from backend
 * Supports both Gemini API and gemini-cli formats
 */
export type SSEEvent =
  // Gemini API format (existing)
  | { session_id: string; type: 'start' }
  | { content: string; type: 'instruction' }
  | { content: string; type: 'chunk' }
  | { session_id: string; token_count: number; type: 'complete' }
  | { error: string; type: 'error' }
  // gemini-cli format (new)
  | { model: string; session_id: string; timestamp: string; type: 'init' }
  | { content: string; role: string; timestamp: string; type: 'message' }
  | {
      parameters: Record<string, unknown>
      timestamp: string
      tool_id: string
      tool_name: string
      type: 'tool_use'
    }
  | {
      status: string
      timestamp: string
      tool_id: string
      type: 'tool_result'
      message?: string
      output?: string
    }
