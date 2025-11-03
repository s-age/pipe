import { useState, useEffect, JSX, useCallback, useMemo } from 'react'

import SessionList from '@/components/organisms/SessionList'
import { SessionMeta } from '@/components/organisms/SessionMeta'
import TurnsList from '@/components/organisms/TurnsList'
import { useStreamingFetch } from '@/hooks/useStreamingFetch'
import { API_BASE_URL } from '@/lib/api/client'
import { deleteSession } from '@/lib/api/session/deleteSession'
import { deleteTodos } from '@/lib/api/session/deleteTodos'
import { deleteTurn } from '@/lib/api/session/deleteTurn'
import { editReferencePersist } from '@/lib/api/session/editReferencePersist'
import { editReferences } from '@/lib/api/session/editReferences'
import { editReferenceTtl } from '@/lib/api/session/editReferenceTtl'
import {
  editSessionMeta,
  EditSessionMetaRequest,
} from '@/lib/api/session/editSessionMeta'
import { editTodos, Todo } from '@/lib/api/session/editTodos'
import { forkSession } from '@/lib/api/session/forkSession'
import { getSession, SessionData } from '@/lib/api/session/getSession'
import { getSessions, SessionOverview } from '@/lib/api/sessions/getSessions'

import { appContainer } from './style.css'

const HomePage = (): JSX.Element => {
  const [sessions, setSessions] = useState<SessionOverview[]>([])
  const [currentSessionId, setCurrentSessionId] = useState<string | null>(null)
  const [sessionData, setSessionData] = useState<SessionData | null>(null)
  const [loading, setLoading] = useState<boolean>(true)
  const [error, setError] = useState<string | null>(null)
  const [streamingTrigger, setStreamingTrigger] = useState<{
    instruction: string
    sessionId: string
  } | null>(null)
  // isStreamingRequestInitiated の削除

  const expertMode = true // 仮の値

  const memoizedStreamingOptions = useMemo((): RequestInit | undefined => {
    if (!streamingTrigger) return undefined

    return {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ instruction: streamingTrigger.instruction }),
    }
  }, [streamingTrigger])

  const {
    streamedText,
    isLoading: isStreaming,
    error: streamingError,
    setStreamedText,
  } = useStreamingFetch(
    streamingTrigger
      ? `${API_BASE_URL}/session/${streamingTrigger.sessionId}/instruction`
      : null,
    memoizedStreamingOptions,
  )

  useEffect((): void => {
    if (streamingError) {
      setError(streamingError)
      setStreamingTrigger(null)
    }
  }, [streamingError])

  useEffect((): void => {
    // 💡 修正されたストリーミング完了判定ロジック
    // streamingTriggerがセットされており、isStreamingが完了し、かつ streamedTextにデータがあるか、
    // または streamingErrorがある場合（ただしstreamingErrorは上のuseEffectで処理される）に実行。
    // isStreamingがfalseになるのを待つことで、リクエストが少なくとも開始したことを保証する。
    if (streamingTrigger && !isStreaming) {
      // 💡 streamingTriggerが設定された直後 (isStreaming=false) の誤発動を防ぐため、
      // 既にデータがあるか、完了していることを前提として処理を続行する。

      const loadSessionDataAfterStreaming = async (): Promise<void> => {
        if (currentSessionId) {
          try {
            const data = await getSession(currentSessionId)
            setSessionData(data.session)
          } catch (err: unknown) {
            setError(
              (err as Error).message || 'Failed to load session data after streaming.',
            )
          }
        }
      }

      // 💡 データ受信後、ストリームが完了したことを確認してからクリアする
      if (streamedText.length > 0 || streamingError) {
        loadSessionDataAfterStreaming()
        setStreamingTrigger(null)
        setStreamedText('')
      }
    }
  }, [
    isStreaming,
    streamingTrigger,
    currentSessionId,
    streamedText,
    streamingError,
    setStreamedText,
  ]) // streamedTextも依存配列に追加

  useEffect((): void => {
    const loadSessions = async (): Promise<void> => {
      try {
        const fetchedSessions = await getSessions()
        setSessions(fetchedSessions.sessions)
        // URLからセッションIDを取得し、現在のセッションを設定
        const pathParts = window.location.pathname.split('/')
        const id = pathParts[pathParts.length - 1]
        if (id && id !== 'session' && id !== '') {
          setCurrentSessionId(id)
        }
      } catch (err: unknown) {
        setError((err as Error).message || 'Failed to load sessions.')
      } finally {
        setLoading(false)
      }
    }
    loadSessions()
  }, [])

  useEffect((): void => {
    const loadSessionData = async (): Promise<void> => {
      if (currentSessionId) {
        setLoading(true)
        try {
          const data = await getSession(currentSessionId)
          setSessionData(data.session)
        } catch (err: unknown) {
          setError((err as Error).message || 'Failed to load session data.')
        }
      } else {
        setSessionData(null)
      }
      setLoading(false) // ロード完了後、必ずfalseに設定
    }
    loadSessionData()
  }, [currentSessionId])

  const handleSessionSelect = (sessionId: string): void => {
    setCurrentSessionId(sessionId)
    window.history.pushState({}, '', `/session/${sessionId}`)
  }

  const handleMetaSave = async (
    id: string,
    meta: EditSessionMetaRequest,
  ): Promise<void> => {
    try {
      await editSessionMeta(id, meta)
      // 必要に応じてセッションデータを再読み込み
      if (currentSessionId === id) {
        const data = await getSession(id)
        setSessionData(data.session)
      }
      const fetchedSessions = await getSessions()
      setSessions(fetchedSessions.sessions)
    } catch (err: unknown) {
      setError((err as Error).message || 'Failed to save session meta.')
    }
  }

  const handleDeleteTurn = async (
    sessionId: string,
    turnIndex: number,
  ): Promise<void> => {
    // confirmをカスタムモーダルに置き換えるべき
    if (!window.confirm('Are you sure you want to delete this turn?')) return
    try {
      await deleteTurn(sessionId, turnIndex)
      // セッションデータを再読み込み
      const data = await getSession(sessionId)
      setSessionData(data.session)
    } catch (err: unknown) {
      setError((err as Error).message || 'Failed to delete turn.')
    }
  }

  const handleForkSession = async (
    sessionId: string,
    forkIndex: number,
  ): Promise<void> => {
    // confirmをカスタムモーダルに置き換えるべき
    if (
      !window.confirm(
        `Are you sure you want to fork this session at turn index ${forkIndex + 1}?`,
      )
    )
      return
    try {
      const result = await forkSession(sessionId, forkIndex)
      if (result.new_session_id) {
        window.location.href = `/session/${result.new_session_id}`
      } else {
        throw new Error('Failed to fork session.')
      }
    } catch (err: unknown) {
      setError((err as Error).message || 'Failed to fork session.')
    }
  }

  const handleSendInstruction = useCallback(
    async (instruction: string): Promise<void> => {
      if (!currentSessionId) return
      console.log('Instruction to send:', instruction)
      setStreamingTrigger({ instruction, sessionId: currentSessionId })
      // isStreamingRequestInitiated の呼び出しを削除
    },
    [currentSessionId, setStreamingTrigger],
  )

  const handleUpdateTodo = async (sessionId: string, todos: Todo[]): Promise<void> => {
    try {
      await editTodos(sessionId, todos)
      // UIは即時更新されるため、ここでは再フェッチしない
    } catch (err: unknown) {
      setError((err as Error).message || 'Failed to update todos.')
    }
  }

  const handleDeleteAllTodos = async (sessionId: string): Promise<void> => {
    // confirmをカスタムモーダルに置き換えるべき
    if (!window.confirm('Are you sure you want to delete all todos for this session?'))
      return
    try {
      await deleteTodos(sessionId)
      // セッションデータを再読み込み
      const data = await getSession(sessionId)
      setSessionData(data.session)
    } catch (err: unknown) {
      setError((err as Error).message || 'Failed to delete all todos.')
    }
  }

  const handleUpdateReferencePersist = async (
    sessionId: string,
    index: number,
    persist: boolean,
  ): Promise<void> => {
    try {
      await editReferencePersist(sessionId, index, persist)
      // セッションデータを再読み込みしてUIを更新
      const data = await getSession(sessionId)
      setSessionData(data.session)
    } catch (err: unknown) {
      setError((err as Error).message || 'Failed to update reference persist state.')
    }
  }

  const handleUpdateReferenceTtl = async (
    sessionId: string,
    index: number,
    ttl: number,
  ): Promise<void> => {
    try {
      await editReferenceTtl(sessionId, index, ttl)
      // セッションデータを再読み込みしてUIを更新
      const data = await getSession(sessionId)
      setSessionData(data.session)
    } catch (err: unknown) {
      setError((err as Error).message || 'Failed to update reference TTL.')
    }
  }

  const handleUpdateReferenceDisabled = async (
    sessionId: string,
    index: number,
    disabled: boolean,
  ): Promise<void> => {
    if (!sessionData) return
    try {
      const newReferences = [...sessionData.references]
      newReferences[index] = { ...newReferences[index], disabled }
      await editReferences(sessionId, newReferences)
      // セッションデータを再読み込みしてUIを更新
      const data = await getSession(sessionId)
      setSessionData(data.session)
    } catch (err: unknown) {
      setError((err as Error).message || 'Failed to update reference disabled state.')
    }
  }

  const handleDeleteSession = async (sessionId: string): Promise<void> => {
    if (!window.confirm('Are you sure you want to delete this session?')) return
    try {
      await deleteSession(sessionId)
      const fetchedSessions = await getSessions()
      setSessions(fetchedSessions.sessions)
      setCurrentSessionId(null)
      setSessionData(null)
      window.history.pushState({}, '', '/') // URLをルートに戻す
    } catch (err: unknown) {
      setError((err as Error).message || 'Failed to delete session.')
    }
  }

  if (loading) {
    return <div className={appContainer}>Loading...</div>
  }

  if (error) {
    return (
      <div className={appContainer} style={{ color: 'red' }}>
        Error: {error}
      </div>
    )
  }

  return (
    <div className={appContainer}>
      <SessionList
        sessions={sessions}
        currentSessionId={currentSessionId}
        onSessionSelect={handleSessionSelect}
      />
      <TurnsList
        sessionData={sessionData}
        currentSessionId={currentSessionId}
        expertMode={expertMode}
        onDeleteTurn={handleDeleteTurn}
        onForkSession={handleForkSession}
        onSendInstruction={handleSendInstruction}
        onDeleteSession={handleDeleteSession}
        streamedText={streamedText}
        isStreaming={isStreaming}
      />
      <SessionMeta
        key={currentSessionId} // currentSessionIdをキーとして追加
        sessionData={sessionData}
        currentSessionId={currentSessionId}
        onMetaSave={handleMetaSave}
        onUpdateTodo={handleUpdateTodo}
        onDeleteAllTodos={handleDeleteAllTodos}
        onUpdateReferencePersist={handleUpdateReferencePersist}
        onUpdateReferenceTtl={handleUpdateReferenceTtl}
        onUpdateReferenceDisabled={handleUpdateReferenceDisabled}
      />
    </div>
  )
}

export default HomePage
