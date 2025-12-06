import { useState } from 'react'

import { useInitialLoading } from '@/hooks/useInitialLoading'
import { getStartSession } from '@/lib/api/bff/getStartSession'
import type { SessionTreeNode } from '@/lib/api/sessionTree/getSessionTree'
import type { Option } from '@/types/option'
import type { Settings } from '@/types/settings'

type UseStartSessionPageLifecycleResult = {
  parentOptions: Option[]
  settings: Settings
  sessionTree: SessionTreeNode[]
  loading: boolean
  error: string | null
  startDefaults?: Record<string, unknown> | null
}

export const useStartSessionPageLifecycle = (): UseStartSessionPageLifecycleResult => {
  const [parentOptions, setParentOptions] = useState<Option[]>([])
  const [settings, setSettings] = useState<
    UseStartSessionPageLifecycleResult['settings'] | null
  >(null)
  const [sessionTree, setSessionTree] = useState<SessionTreeNode[]>([])
  const [error, setError] = useState<string | null>(null)
  const [loading, setLoading] = useState<boolean>(true)
  const [startDefaults, setStartDefaults] = useState<Record<string, unknown> | null>(
    null
  )

  const loadData = async (): Promise<void> => {
    try {
      const response = await getStartSession()
      // Normalize `session_tree` into a flat `Option[]` for selects.
      // The backend may return either an array of tuples `[id, overview]`
      // or a nested tree of nodes. Flatten both shapes defensively and
      // prefix child labels with indentation according to depth.
      const indentForDepth = (d: number): string => ' '.repeat(Math.max(0, d) * 2)

      const out: Option[] = []

      const push = (id: unknown, overview: unknown, depth = 0): void => {
        const overviewRec = overview as Record<string, unknown> | undefined
        const purpose = overviewRec?.purpose
        const sessionId = String(overviewRec?.sessionId || id || '')
        const label =
          typeof purpose === 'string' && purpose.trim() ? purpose : sessionId
        out.push({
          value: String(id ?? ''),
          label: `${indentForDepth(depth)}${label}`
        })
      }

      const flatten = (nodes: unknown[], depth = 0): void => {
        if (!Array.isArray(nodes)) return
        for (const n of nodes) {
          // Tuple form: [id, overview, maybeChildren]
          if (Array.isArray(n) && n.length >= 2) {
            const tuple = n as unknown[]
            push(tuple[0], tuple[1], depth)
            if (Array.isArray(tuple[2])) {
              flatten(tuple[2] as unknown[], depth + 1)
            }
            continue
          }

          // Node form: { sessionId, overview, children }
          if (
            n &&
            typeof n === 'object' &&
            'sessionId' in (n as Record<string, unknown>)
          ) {
            const node = n as Record<string, unknown>
            push(node.sessionId, node.overview ?? node, depth)
            if (
              Array.isArray(node.children) &&
              (node.children as unknown[]).length > 0
            ) {
              flatten(node.children as unknown[], depth + 1)
            }
            continue
          }

          // Option-like: { value, label }
          if (
            n &&
            typeof n === 'object' &&
            'value' in (n as Record<string, unknown>) &&
            'label' in (n as Record<string, unknown>)
          ) {
            const opt = n as Record<string, unknown>
            out.push({
              value: String(opt.value ?? ''),
              label: `${indentForDepth(0)}${String(opt.label ?? '')}`
            })
            continue
          }

          // Primitive fallback
          if (n !== null && n !== undefined) {
            out.push({ value: String(n), label: String(n) })
          }
        }
      }

      flatten(response.sessionTree as unknown[])
      setParentOptions(out)
      setSettings(response.settings)
      setStartDefaults({
        sessionId: '',
        purpose: '',
        background: '',
        roles: [],
        parent: null,
        references: [],
        artifacts: [],
        procedure: null,
        instruction: '',
        multiStepReasoningEnabled: false,
        hyperparameters: response.settings.hyperparameters,
        todos: []
      })
      setSessionTree(response.sessionTree)
    } catch (error_: unknown) {
      setError((error_ as Error).message || 'Failed to load initial data.')
    } finally {
      setLoading(false)
    }
  }

  useInitialLoading(loadData)

  return {
    parentOptions,
    settings: settings!,
    sessionTree,
    loading,
    error,
    startDefaults
  }
}
