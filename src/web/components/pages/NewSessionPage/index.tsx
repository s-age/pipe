import { useState, useEffect, JSX } from 'react'

import NewSessionForm from '@/components/organisms/NewSessionForm'
import { createSession, fetchSessions, fetchSettings } from '@/lib/api_client/client'

import { pageContainer, errorMessageStyle } from './style.css'

type SessionOption = {
  value: string
  label: string
}

type DefaultSettings = {
  parameters?: {
    temperature?: { value: number }
    top_p?: { value: number }
    top_k?: { value: number }
  }
}

type SessionMetaType = {
  purpose: string
  [key: string]: string | number | boolean | object | null | undefined
}

type NewSessionFormInputs = {
  purpose: string
  background: string
  roles?: string
  parent?: string
  references?: string
  artifacts?: string
  procedure?: string
  instruction: string
  multi_step_reasoning_enabled: boolean
  hyperparameters?: {
    temperature: number
    top_p: number
    top_k: number
  }
}

const NewSessionPage: () => JSX.Element = () => {
  const [sessions, setSessions] = useState<SessionOption[]>([])
  const [settings, setSettings] = useState<DefaultSettings | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [loading, setLoading] = useState<boolean>(true)

  useEffect(() => {
    const loadData = async () => {
      try {
        const [sessionsData, settingsData] = await Promise.all([
          fetchSessions(),
          fetchSettings(),
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

  const handleSubmit = async (data: NewSessionFormInputs) => {
    setError(null)
    try {
      const result = await createSession(data)
      if (result.success) {
        window.location.href = `/session/${result.session_id}`
      } else {
        setError(result.message || 'Failed to create session.')
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
      <NewSessionForm
        onSubmit={handleSubmit}
        sessions={sessions}
        defaultSettings={settings}
      />
      {error && <p className={errorMessageStyle}>{error}</p>}
    </div>
  )
}

export default NewSessionPage
