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
 */
export type SSEEvent =
  | { type: 'start'; session_id: string }
  | { type: 'instruction'; content: string }
  | { type: 'chunk'; content: string }
  | { type: 'complete'; session_id: string; token_count: number }
  | { type: 'error'; error: string }
