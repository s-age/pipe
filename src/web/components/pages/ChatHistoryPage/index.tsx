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
import useSessionStore from '@/stores/useChatHistoryStore'

import { appContainer } from './style.css'

const HomePage = (): JSX.Element => {
  const { state, actions } = useSessionStore()
  const {
    sessionTree: { sessions, currentSessionId },
    sessionDetail,
    error,
  } = state

  const {
    setSessions,
    setCurrentSessionId,
    setSessionDetail,
    selectSession,
    setError,
    refreshSessions,
  } = actions

  // Initial session loading
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
        // currentSessionIdがまだ設定されていない場合にのみURLからのIDを設定
        if (id && id !== 'session' && id !== '' && !currentSessionId) {
          setCurrentSessionId(id)
        }
        setError(null)
      } catch (err: unknown) {
        setError((err as Error).message || 'Failed to load sessions.')
      }
    }
    loadSessions()
  }, [setSessions, setCurrentSessionId, setError, currentSessionId]) // 必要な個々の関数とcurrentSessionIdを依存配列に

  // Load session detail when currentSessionId changes
  useEffect(() => {
    const loadSessionDetail = async (): Promise<void> => {
      if (currentSessionId) {
        try {
          const data = await getSession(currentSessionId)
          setSessionDetail(data.session)
          setError(null)
        } catch (err: unknown) {
          setError((err as Error).message || 'Failed to load session data.')
        }
      } else {
        setSessionDetail(null)
      }
    }
    loadSessionDetail()
  }, [currentSessionId, setSessionDetail, setError]) // 必要な個々の関数を依存配列に

  const handleMetaSave = async (
    id: string,
    meta: EditSessionMetaRequest,
  ): Promise<void> => {
    try {
      await editSessionMeta(id, meta)
      await refreshSessions()
      setError(null)
    } catch (err: unknown) {
      setError((err as Error).message || 'Failed to save session meta.')
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
        selectSession={selectSession}
        setError={setError}
      />
      <ChatHistory
        currentSessionId={currentSessionId}
        sessionDetail={sessionDetail}
        expertMode={expertMode}
        setSessionDetail={setSessionDetail}
        setError={setError}
        refreshSessions={refreshSessions}
      />
      <SessionMeta
        key={currentSessionId}
        sessionDetail={sessionDetail}
        currentSessionId={currentSessionId}
        onMetaSave={handleMetaSave}
        setSessionDetail={setSessionDetail}
        setError={setError}
        refreshSessions={refreshSessions}
      />
    </div>
  )
}

export default HomePage
