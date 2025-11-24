import type {
  SessionOverview,
  SessionTreeNode
} from '@/lib/api/sessionTree/getSessionTree'

// A session node returned by the backend can be either a legacy pair
// `[id, overview]` or the newer hierarchical `SessionTreeNode`.
export type SessionPair = [string, SessionOverview]
export type SessionNode = SessionPair | SessionTreeNode

export const isSessionPair = (node: unknown): node is SessionPair =>
  Array.isArray(node) &&
  node.length === 2 &&
  typeof node[0] === 'string' &&
  typeof node[1] === 'object' &&
  node[1] !== null
