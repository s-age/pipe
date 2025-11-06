import { useCallback, useReducer } from 'react'

import { SessionDetail } from '@/lib/api/session/getSession'
import { getSessions, SessionOverview } from '@/lib/api/sessions/getSessions'

export type SessionTree = {
  sessions: SessionOverview[]
  currentSessionId: string | null
}

export type Settings = Record<string, unknown>

export type State = {
  sessionTree: SessionTree
  sessionDetail: SessionDetail | null
  settings: Settings
  error: string | null
}

export const initialState: State = {
  sessionTree: { sessions: [], currentSessionId: null },
  sessionDetail: null,
  settings: {},
  error: null,
}

export type Action =
  | { type: 'SET_SESSIONS'; payload: SessionOverview[] }
  | { type: 'SET_CURRENT_SESSION_ID'; payload: string | null }
  | { type: 'SET_SESSION_DETAIL'; payload: SessionDetail | null }
  | {
      type: 'SET_SESSION_AND_CURRENT'
      payload: { id: string | null; detail: SessionDetail | null }
    }
  | { type: 'UPDATE_SETTINGS'; payload: Partial<Settings> }
  | { type: 'SET_ERROR'; payload: string | null }
  | { type: 'RESET' }

export const reducer = (state: State, action: Action): State => {
  switch (action.type) {
    case 'SET_SESSIONS':
      return {
        ...state,
        sessionTree: { ...state.sessionTree, sessions: action.payload },
      }
    case 'SET_CURRENT_SESSION_ID':
      return {
        ...state,
        sessionTree: { ...state.sessionTree, currentSessionId: action.payload },
      }
    case 'SET_SESSION_DETAIL':
      return {
        ...state,
        sessionDetail: action.payload,
      }
    case 'SET_SESSION_AND_CURRENT':
      return {
        ...state,
        sessionTree: { ...state.sessionTree, currentSessionId: action.payload.id },
        sessionDetail: action.payload.detail,
      }
    case 'UPDATE_SETTINGS':
      return {
        ...state,
        settings: { ...state.settings, ...action.payload },
      }
    case 'SET_ERROR':
      return {
        ...state,
        error: action.payload,
      }
    case 'RESET':
      return initialState
    default:
      return state
  }
}

export type Actions = {
  setSessions: (sessions: SessionOverview[]) => void
  setCurrentSessionId: (id: string | null) => void
  setSessionDetail: (detail: SessionDetail | null) => void
  selectSession: (id: string | null, detail: SessionDetail | null) => void
  updateSettings: (partial: Partial<Settings>) => void
  setError: (error: string | null) => void
  refreshSessions: () => Promise<void>
  reset: () => void
}

export type UseSessionStoreReturn = {
  state: State
  actions: Actions
}

export const useSessionStore = (initial?: Partial<State>): UseSessionStoreReturn => {
  const mergedInitial: State = { ...initialState, ...(initial || {}) }
  const [state, dispatch] = useReducer(reducer, mergedInitial)

  const setSessions = useCallback((sessions: SessionOverview[]) => {
    dispatch({ type: 'SET_SESSIONS', payload: sessions })
  }, [])

  const setCurrentSessionId = useCallback((id: string | null) => {
    dispatch({ type: 'SET_CURRENT_SESSION_ID', payload: id })
  }, [])

  const setSessionDetail = useCallback((detail: SessionDetail | null) => {
    dispatch({ type: 'SET_SESSION_DETAIL', payload: detail })
  }, [])

  const selectSession = useCallback(
    (id: string | null, detail: SessionDetail | null) => {
      dispatch({ type: 'SET_SESSION_AND_CURRENT', payload: { id, detail } })
    },
    [],
  )

  const updateSettings = useCallback((partial: Partial<Settings>) => {
    dispatch({ type: 'UPDATE_SETTINGS', payload: partial })
  }, [])

  const setError = useCallback((error: string | null) => {
    dispatch({ type: 'SET_ERROR', payload: error })
  }, [])

  const refreshSessions = useCallback(async (): Promise<void> => {
    try {
      const fetchedSessions = await getSessions()
      dispatch({
        type: 'SET_SESSIONS',
        payload: fetchedSessions.sessions.map(([id, session]) => ({
          ...session,
          session_id: id,
        })),
      })
      setError(null)
    } catch (err: unknown) {
      setError((err as Error).message || 'Failed to refresh sessions.')
    }
  }, [setError])

  const reset = useCallback(() => dispatch({ type: 'RESET' }), [])

  return {
    state,
    actions: {
      setSessions,
      setCurrentSessionId,
      setSessionDetail,
      selectSession,
      updateSettings,
      setError,
      refreshSessions,
      reset,
    },
  }
}

export default useSessionStore
