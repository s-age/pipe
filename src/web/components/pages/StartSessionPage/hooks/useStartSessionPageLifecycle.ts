import { useState } from 'react'

import { useInitialLoading } from '@/hooks/useInitialLoading'
import { getStartSession } from '@/lib/api/bff/getStartSession'
import type { SessionTreeNode } from '@/lib/api/sessionTree/getSessionTree'
import type { Option } from '@/types/option'
import type { Settings } from '@/types/settings'

import { normalizeSessionTreeToOptions } from './normalizeSessionTree'

type UseStartSessionPageLifecycleResult = {
  parentOptions: Option[]
  settings: Settings | null
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

      // Normalize session tree to options using utility function
      const parentOptions = normalizeSessionTreeToOptions(
        response.sessionTree as unknown[]
      )

      setParentOptions(parentOptions)
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
    settings,
    sessionTree,
    loading,
    error,
    startDefaults
  }
}
