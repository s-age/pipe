import { useState, useEffect } from 'react'

import { getSessionTree, SessionOverview } from '@/lib/api/sessionTree/getSessions'
import { getSettings, Settings } from '@/lib/api/settings/getSettings'

type SessionOption = {
  value: string
  label: string
}

type UseSessionDetailResult = {
  sessions: SessionOption[]
  settings: Settings | null
  loading: boolean
  error: string | null
}

export const useSessionDetail = (): UseSessionDetailResult => {
  const [sessions, setSessions] = useState<SessionOption[]>([])
  const [settings, setSettings] = useState<Settings | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [loading, setLoading] = useState<boolean>(true)

  useEffect(() => {
    const loadData = async (): Promise<void> => {
      try {
        const [sessionsResponse, settingsData] = await Promise.all([
          getSessionTree(),
          getSettings(),
        ])
        setSessions(
          sessionsResponse.sessions.map(([, session]: [string, SessionOverview]) => ({
            value: session.session_id,
            label: session.purpose,
          })),
        )
        setSettings(settingsData)
      } catch (err: unknown) {
        setError((err as Error).message || 'Failed to load initial data.')
      } finally {
        setLoading(false)
      }
    }
    loadData()
  }, [])

  return { sessions, settings, loading, error }
}
