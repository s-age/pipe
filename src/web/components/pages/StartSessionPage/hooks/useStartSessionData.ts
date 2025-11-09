import { useState, useEffect } from 'react'

import type { SessionOverview } from '@/lib/api/sessionTree/getSessionTree'
import { getSessionTree } from '@/lib/api/sessionTree/getSessionTree'
import { getSettings } from '@/lib/api/settings/getSettings'
import type { SessionOption } from '@/types/session'
import type { Settings } from '@/types/settings'

type UseStartSessionDataResult = {
  sessionTree: SessionOption[]
  settings: Settings | null
  loading: boolean
  error: string | null
}

export const useStartSessionData = (): UseStartSessionDataResult => {
  const [sessionTree, setSessionTree] = useState<SessionOption[]>([])
  const [settings, setSettings] = useState<Settings | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [loading, setLoading] = useState<boolean>(true)

  useEffect(() => {
    const loadData = async (): Promise<void> => {
      try {
        const [sessionsResponse, settingsData] = await Promise.all([
          getSessionTree(),
          getSettings()
        ])
        setSessionTree(
          sessionsResponse.sessions.map(([, session]: [string, SessionOverview]) => ({
            value: session.session_id,
            label: session.purpose
          }))
        )
        setSettings(settingsData)
      } catch (error_: unknown) {
        setError((error_ as Error).message || 'Failed to load initial data.')
      } finally {
        setLoading(false)
      }
    }
    loadData()
  }, [])

  return { sessionTree, settings, loading, error }
}
