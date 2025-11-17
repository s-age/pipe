import { useState, useEffect } from 'react'

import { getStartSessionSettings } from '@/lib/api/bff/getStartSessionSettings'
import type { SessionOverview } from '@/lib/api/sessionTree/getSessionTree'
import type { Option } from '@/types/option'
import type { Settings } from '@/types/settings'

type UseStartSessionPageLifecycleResult = {
  parentOptions: Option[]
  settings: Settings
  sessionTree: [string, SessionOverview][]
  loading: boolean
  error: string | null
  startDefaults?: Record<string, unknown> | null
}

export const useStartSessionPageLifecycle = (): UseStartSessionPageLifecycleResult => {
  const [parentOptions, setParentOptions] = useState<Option[]>([])
  const [settings, setSettings] = useState<
    UseStartSessionPageLifecycleResult['settings'] | null
  >(null)
  const [sessionTree, setSessionTree] = useState<[string, SessionOverview][]>([])
  const [error, setError] = useState<string | null>(null)
  const [loading, setLoading] = useState<boolean>(true)
  const [startDefaults, setStartDefaults] = useState<Record<string, unknown> | null>(
    null
  )

  useEffect(() => {
    const loadData = async (): Promise<void> => {
      try {
        const response = await getStartSessionSettings()
        setParentOptions(
          response.session_tree.map(([id, session]: [string, SessionOverview]) => ({
            value: id,
            label: session.purpose
          }))
        )
        setSettings(response.settings)
        setStartDefaults({
          session_id: '',
          purpose: '',
          background: '',
          roles: [],
          parent: null,
          references: [],
          artifacts: [],
          procedure: null,
          instruction: '',
          multi_step_reasoning_enabled: false,
          hyperparameters: response.settings.hyperparameters,
          todos: []
        })
        setSessionTree(response.session_tree)
      } catch (error_: unknown) {
        setError((error_ as Error).message || 'Failed to load initial data.')
      } finally {
        setLoading(false)
      }
    }
    loadData()
  }, [])

  return {
    parentOptions,
    settings: settings!,
    sessionTree,
    loading,
    error,
    startDefaults
  }
}
