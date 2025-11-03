import { useState, useEffect, JSX } from 'react'

import StartSessionForm from '@/components/organisms/StartSessionForm'
import { startSession, StartSessionRequest } from '@/lib/api/session/startSession'
import { getSessions, SessionMetaType } from '@/lib/api/sessions/getSessions'
import { getSettings, Settings } from '@/lib/api/settings/getSettings'

import { pageContainer, errorMessageStyle } from './style.css'

type SessionOption = {
  value: string
  label: string
}

const StartSessionPage: () => JSX.Element = () => {
  const [sessions, setSessions] = useState<SessionOption[]>([])
  const [settings, setSettings] = useState<Settings | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [loading, setLoading] = useState<boolean>(true)

  useEffect(() => {
    const loadData = async () => {
      try {
        const [sessionsData, settingsData] = await Promise.all([
          getSessions(),
          getSettings(),
        ])
        setSessions(
          sessionsData.map((s: [string, SessionMetaType]) => ({
            value: s[0],
            label: s[1].purpose,
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

  const handleSubmit = async (data: StartSessionRequest) => {
    setError(null)
    try {
      const result = await startSession(data)
      if (result.session_id) {
        window.location.href = `/session/${result.session_id}`
      } else {
        setError('Failed to create session: No session ID returned.')
      }
    } catch (err: unknown) {
      setError((err as Error).message || 'An error occurred during session creation.')
    }
  }

  if (loading) {
    return <div className={pageContainer}>Loading...</div>
  }

  if (error && !loading) {
    return (
      <div className={pageContainer}>
        <p className={errorMessageStyle}>{error}</p>
      </div>
    )
  }

  return (
    <div className={pageContainer}>
      <StartSessionForm
        onSubmit={handleSubmit}
        sessions={sessions}
        defaultSettings={settings}
      />
      {error && <p className={errorMessageStyle}>{error}</p>}
    </div>
  )
}

export default StartSessionPage
