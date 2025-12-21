/* eslint-disable no-snake-case-properties/no-snake-case-properties */
/**
 * Chat segment types for streaming display
 */

export type ChatSegment =
  | { type: 'text'; content: string; isComplete: boolean }
  | {
      type: 'tool'
      content: string
      name?: string
      status?: 'running' | 'completed' | 'succeeded' | 'failed'
      isComplete: boolean
    }

/**
 * SSE event types from backend
 * Supports both Gemini API and gemini-cli formats
 */
export type SSEEvent =
  // Gemini API format (existing)
  | { type: 'start'; session_id: string }
  | { type: 'instruction'; content: string }
  | { type: 'chunk'; content: string }
  | { type: 'complete'; session_id: string; token_count: number }
  | { type: 'error'; error: string }
  // gemini-cli format (new)
  | { type: 'init'; timestamp: string; session_id: string; model: string }
  | { type: 'message'; timestamp: string; role: string; content: string }
  | {
      type: 'tool_use'
      timestamp: string
      tool_name: string
      tool_id: string
      parameters: Record<string, unknown>
    }
  | {
      type: 'tool_result'
      timestamp: string
      tool_id: string
      status: string
      output?: string
      message?: string
    }
