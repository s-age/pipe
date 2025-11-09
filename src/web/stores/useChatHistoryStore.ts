import { useCallback, useReducer, useEffect, useRef } from 'react'

import type { SessionDetail } from '@/lib/api/session/getSession'
import type { SessionOverview } from '@/lib/api/sessionTree/getSessionTree'
import { getSessionTree } from '@/lib/api/sessionTree/getSessionTree'

export type SessionTree = {
  sessions: SessionOverview[]
  currentSessionId: string | null
}

import type { Settings } from '../types/settings'

export type State = {
  sessionTree: SessionTree
  sessionDetail: SessionDetail | null
  settings: Settings
}

export const initialState: State = {
  sessionTree: { sessions: [], currentSessionId: null },
  sessionDetail: null,
  settings: { parameters: { temperature: null, top_p: null, top_k: null } }
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
  | { type: 'RESET' }

export const reducer = (state: State, action: Action): State => {
  switch (action.type) {
    case 'SET_SESSIONS':
      return {
        ...state,
        sessionTree: { ...state.sessionTree, sessions: action.payload }
      }
    case 'SET_CURRENT_SESSION_ID':
      return {
        ...state,
        sessionTree: { ...state.sessionTree, currentSessionId: action.payload }
      }
    case 'SET_SESSION_DETAIL':
      return {
        ...state,
        sessionDetail: action.payload
      }
    case 'SET_SESSION_AND_CURRENT':
      return {
        ...state,
        sessionTree: { ...state.sessionTree, currentSessionId: action.payload.id },
        sessionDetail: action.payload.detail
      }
    case 'UPDATE_SETTINGS':
      return {
        ...state,
        settings: { ...state.settings, ...action.payload }
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

  // Keep a ref to the current sessions array so callbacks (like refreshSessions)
  // can read the latest value without closing over `state` and changing
  // their identity when the sessions change. This prevents effects that
  // depend on `refreshSessions` from re-running just because the function
  // identity changed.
  const sessionsReference = useRef<SessionOverview[]>(state.sessionTree.sessions)
  useEffect(() => {
    sessionsReference.current = state.sessionTree.sessions
  }, [state.sessionTree.sessions])

  const selectSession = useCallback(
    (id: string | null, detail: SessionDetail | null) => {
      dispatch({ type: 'SET_SESSION_AND_CURRENT', payload: { id, detail } })
    },
    []
  )

  const updateSettings = useCallback((partial: Partial<Settings>) => {
    dispatch({ type: 'UPDATE_SETTINGS', payload: partial })
  }, [])

  const refreshSessions = useCallback(async (): Promise<void> => {
    const fetchedSessions = await getSessionTree()
    const newSessions = fetchedSessions.sessions.map(([id, session]) => ({
      ...session,
      session_id: id
    }))

    // Only update the store if sessions actually changed to avoid
    // retriggering dependent effects (prevents potential refresh loops).
    const old = sessionsReference.current
    const equal =
      old.length === newSessions.length &&
      old.every((s, i) => s.session_id === newSessions[i].session_id)

    if (!equal) {
      dispatch({ type: 'SET_SESSIONS', payload: newSessions })
    }
  }, [])

  const reset = useCallback(() => dispatch({ type: 'RESET' }), [])

  return {
    state,
    actions: {
      setSessions,
      setCurrentSessionId,
      setSessionDetail,
      selectSession,
      updateSettings,

      refreshSessions,
      reset
    }
  }
}
