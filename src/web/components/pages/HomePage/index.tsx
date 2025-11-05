import { JSX, useEffect } from 'react'

import ChatHistory from '@/components/organisms/ChatHistory'
import { SessionMeta } from '@/components/organisms/SessionMeta'
import SessionTree from '@/components/organisms/SessionTree'
import {
  editSessionMeta,
  EditSessionMetaRequest,
} from '@/lib/api/session/editSessionMeta'
import { getSession } from '@/lib/api/session/getSession'
import { getSessions } from '@/lib/api/sessions/getSessions'
import useSessionStore from '@/stores/useHomeStore'

import { appContainer } from './style.css'

const HomePage = (): JSX.Element => {
  const { state, actions } = useSessionStore()
  const {
    sessionTree: { sessions, currentSessionId },
    sessionDetail,
    error,
  } = state

  // Initial session loading
  useEffect(() => {
    const loadSessions = async (): Promise<void> => {
      try {
        const fetchedSessions = await getSessions()
        actions.setSessions(
          fetchedSessions.sessions.map(([id, session]) => ({
            ...session,
            session_id: id,
          })),
        )
        const pathParts = window.location.pathname.split('/')
        const id = pathParts[pathParts.length - 1]
        if (id && id !== 'session' && id !== '') {
          actions.setCurrentSessionId(id)
        }
        actions.setError(null)
      } catch (err: unknown) {
        actions.setError((err as Error).message || 'Failed to load sessions.')
      }
    }
    loadSessions()
  }, [actions])

  // Load session detail when currentSessionId changes
  useEffect(() => {
    const loadSessionDetail = async (): Promise<void> => {
      if (currentSessionId) {
        try {
          const data = await getSession(currentSessionId)
          actions.setSessionDetail(data.session)
          actions.setError(null)
        } catch (err: unknown) {
          actions.setError((err as Error).message || 'Failed to load session data.')
        }
      } else {
        actions.setSessionDetail(null)
      }
    }
    loadSessionDetail()
  }, [currentSessionId, actions])

  const handleMetaSave = async (
    id: string,
    meta: EditSessionMetaRequest,
  ): Promise<void> => {
    try {
      await editSessionMeta(id, meta)
      await actions.refreshSessions()
      actions.setError(null)
    } catch (err: unknown) {
      actions.setError((err as Error).message || 'Failed to save session meta.')
    }
  }

  const expertMode = (state.settings.expertMode as boolean) ?? true

  if (error) {
    return (
      <div className={appContainer} style={{ color: 'red' }}>
        Error: {error}
      </div>
    )
  }

  return (
    <div className={appContainer}>
      <SessionTree
        sessions={sessions}
        currentSessionId={currentSessionId}
        selectSession={actions.selectSession}
        setError={actions.setError}
      />
      <ChatHistory
        currentSessionId={currentSessionId}
        sessionDetail={sessionDetail}
        expertMode={expertMode}
        setSessionDetail={actions.setSessionDetail}
        setError={actions.setError}
        refreshSessions={actions.refreshSessions}
      />
      <SessionMeta
        key={currentSessionId}
        sessionDetail={sessionDetail}
        currentSessionId={currentSessionId}
        onMetaSave={handleMetaSave}
        setSessionDetail={actions.setSessionDetail}
        setError={actions.setError}
        refreshSessions={actions.refreshSessions}
      />
    </div>
  )
}

export default HomePage
