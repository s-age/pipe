import { useState, useEffect } from 'react'

import { getSessions, SessionOverview } from '@/lib/api/sessions/getSessions'
import { getSettings, Settings } from '@/lib/api/settings/getSettings'

type SessionOption = {
  value: string
  label: string
}

type UseSessionDataResult = {
  sessions: SessionOption[]
  settings: Settings | null
  loading: boolean
  error: string | null
}

export const useSessionData = (): UseSessionDataResult => {
  const [sessions, setSessions] = useState<SessionOption[]>([])
  const [settings, setSettings] = useState<Settings | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [loading, setLoading] = useState<boolean>(true)

  useEffect(() => {
    const loadData = async (): Promise<void> => {
      try {
        const [sessionsResponse, settingsData] = await Promise.all([
          getSessions(),
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
