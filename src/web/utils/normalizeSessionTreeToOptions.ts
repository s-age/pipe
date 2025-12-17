import type { Option } from '@/types/option'

type SessionTreeTuple = [string, Record<string, unknown>, unknown[]?]
type SessionTreeNodeObject = {
  sessionId: string
  overview?: Record<string, unknown>
  children?: unknown[]
}
type OptionLike = {
  value: string | number
  label: string
}

const isTuple = (value: unknown): value is SessionTreeTuple =>
  Array.isArray(value) && value.length >= 2

const isNodeObject = (value: unknown): value is SessionTreeNodeObject =>
  typeof value === 'object' && value !== null && 'sessionId' in value

const isOptionLike = (value: unknown): value is OptionLike =>
  typeof value === 'object' && value !== null && 'value' in value && 'label' in value

/**
 * Normalizes session tree data to Option[] format
 *
 * Converts multiple formats (tuple, node, option) returned from backend
 * into a unified Option[] format with indentation for hierarchy
 */
export const normalizeSessionTreeToOptions = (sessionTree: unknown[]): Option[] => {
  const indentForDepth = (d: number): string => ' '.repeat(Math.max(0, d) * 2)
  const out: Option[] = []

  const push = (id: unknown, overview: unknown, depth = 0): void => {
    const overviewRec = overview as Record<string, unknown> | undefined
    const purpose = overviewRec?.purpose
    const sessionId = String(overviewRec?.sessionId || id || '')
    const label = typeof purpose === 'string' && purpose.trim() ? purpose : sessionId
    out.push({
      value: String(id ?? ''),
      label: `${indentForDepth(depth)}${label}`
    })
  }

  const flatten = (nodes: unknown[], depth = 0): void => {
    if (!Array.isArray(nodes)) return
    for (const n of nodes) {
      // Tuple form: [id, overview, maybeChildren]
      if (isTuple(n)) {
        push(n[0], n[1], depth)
        if (Array.isArray(n[2])) {
          flatten(n[2], depth + 1)
        }
        continue
      }

      // Node form: { sessionId, overview, children }
      if (isNodeObject(n)) {
        push(n.sessionId, n.overview ?? n, depth)
        if (Array.isArray(n.children) && n.children.length > 0) {
          flatten(n.children, depth + 1)
        }
        continue
      }

      // Option-like: { value, label }
      if (isOptionLike(n)) {
        out.push({
          value: String(n.value),
          label: `${indentForDepth(0)}${n.label}`
        })
        continue
      }

      // Primitive fallback
      if (n !== null && n !== undefined) {
        out.push({ value: String(n), label: String(n) })
      }
    }
  }

  flatten(sessionTree)

  return out
}
