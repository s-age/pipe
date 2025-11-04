import { useState, useEffect, useCallback } from 'react'

import { deleteSession } from '@/lib/api/session/deleteSession'
import {
  editSessionMeta,
  EditSessionMetaRequest,
} from '@/lib/api/session/editSessionMeta'
import { getSession, SessionDetail } from '@/lib/api/session/getSession'
import { getSessions, SessionOverview } from '@/lib/api/sessions/getSessions'

type UseSessionManagement = {
  sessions: SessionOverview[]
  currentSessionId: string | null
  sessionDetail: SessionDetail | null
  error: string | null
  setCurrentSessionId: (id: string | null) => void
  handleSessionSelect: (sessionId: string) => void
  handleMetaSave: (id: string, meta: EditSessionMetaRequest) => Promise<void>
  handleDeleteSession: (sessionId: string) => Promise<void>
  setSessionDetail: (data: SessionDetail | null) => void
}

export const useSessionManagement = (): UseSessionManagement => {
  const [sessions, setSessions] = useState<SessionOverview[]>([])
  const [currentSessionId, setCurrentSessionId] = useState<string | null>(null)
  const [sessionDetail, setSessionDetail] = useState<SessionDetail | null>(null)
  const [error, setError] = useState<string | null>(null)

  // セッション一覧のロード
  useEffect(() => {
    const loadSessions = async (): Promise<void> => {
      try {
        const fetchedSessions = await getSessions()
        setSessions(
          fetchedSessions.sessions.map(([id, session]) => ({
            ...session,
            session_id: id,
          })),
        )
        const pathParts = window.location.pathname.split('/')
        const id = pathParts[pathParts.length - 1]
        if (id && id !== 'session' && id !== '') {
          setCurrentSessionId(id)
        }
      } catch (err: unknown) {
        setError((err as Error).message || 'Failed to load sessions.')
      }
    }
    loadSessions()
  }, [])

  // 現在のセッションデータのロード
  useEffect(() => {
    const loadSessionDetail = async (): Promise<void> => {
      if (currentSessionId) {
        try {
          const data = await getSession(currentSessionId)
          setSessionDetail(data.session)
        } catch (err: unknown) {
          setError((err as Error).message || 'Failed to load session data.')
        }
      } else {
        setSessionDetail(null)
      }
    }
    loadSessionDetail()
  }, [currentSessionId])

  const handleSessionSelect = useCallback(
    (sessionId: string): void => {
      setCurrentSessionId(sessionId)
      window.history.replaceState({}, '', `/session/${sessionId}`)
    },
    [setCurrentSessionId],
  )

  const handleMetaSave = useCallback(
    async (id: string, meta: EditSessionMetaRequest): Promise<void> => {
      try {
        await editSessionMeta(id, meta)
        if (currentSessionId === id) {
          const data = await getSession(id)
          setSessionDetail(data.session)
        }
        const fetchedSessions = await getSessions()
        setSessions(fetchedSessions.sessions.map(([, session]) => session))
      } catch (err: unknown) {
        setError((err as Error).message || 'Failed to save session meta.')
      }
    },
    [currentSessionId, setSessionDetail],
  )

  const handleDeleteSession = useCallback(
    async (sessionId: string): Promise<void> => {
      if (!window.confirm('Are you sure you want to delete this session?')) return
      try {
        await deleteSession(sessionId)
        const fetchedSessions = await getSessions()
        setSessions(fetchedSessions.sessions.map(([, session]) => session))
        setCurrentSessionId(null)
        setSessionDetail(null)
        window.history.pushState({}, '', '/')
      } catch (err: unknown) {
        setError((err as Error).message || 'Failed to delete session.')
      }
    },
    [setSessions, setCurrentSessionId, setSessionDetail],
  )

  return {
    sessions,
    currentSessionId,
    sessionDetail,
    error,
    setCurrentSessionId,
    handleSessionSelect,
    handleMetaSave,
    handleDeleteSession,
    setSessionDetail,
  }
}
