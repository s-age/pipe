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
}

export const useStartSessionPageLifecycle = (): UseStartSessionPageLifecycleResult => {
  const [parentOptions, setParentOptions] = useState<Option[]>([])
  const [settings, setSettings] = useState<
    UseStartSessionPageLifecycleResult['settings'] | null
  >(null)
  const [sessionTree, setSessionTree] = useState<[string, SessionOverview][]>([])
  const [error, setError] = useState<string | null>(null)
  const [loading, setLoading] = useState<boolean>(true)

  useEffect(() => {
    const loadData = async (): Promise<void> => {
      try {
        const response = await getStartSessionSettings()
        setParentOptions(
          response.session_tree.map(([, session]: [string, SessionOverview]) => ({
            value: session.session_id,
            label: session.purpose
          }))
        )
        setSettings(response.settings)
        setSessionTree(response.session_tree)
      } catch (error_: unknown) {
        setError((error_ as Error).message || 'Failed to load initial data.')
      } finally {
        setLoading(false)
      }
    }
    loadData()
  }, [])

  return { parentOptions, settings: settings!, sessionTree, loading, error }
}
