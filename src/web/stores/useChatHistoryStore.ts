import { useCallback, useReducer } from 'react'

import type { RoleOption } from '@/lib/api/roles/getRoles'
import type { SessionDetail } from '@/lib/api/session/getSession'
import type {
  SessionOverview,
  SessionTreeNode
} from '@/lib/api/sessionTree/getSessionTree'

export type SessionTree = {
  // sessions may be either a flat list of SessionOverview or a hierarchical
  // tree of SessionTreeNode objects produced by the backend.
  sessions: SessionOverview[] | SessionTreeNode[]
  currentSessionId: string | null
}

import type { Settings } from '../types/settings'

export type State = {
  sessionTree: SessionTree
  sessionDetail: SessionDetail | null
  settings: Settings
  roleOptions: RoleOption[]
  archivedSessions: SessionOverview[]
}

export const initialState: State = {
  sessionTree: { sessions: [], currentSessionId: null },
  sessionDetail: null,
  settings: {
    hyperparameters: { temperature: null, top_p: null, top_k: null }
  } as Settings,
  roleOptions: [],
  archivedSessions: []
}

export type Action =
  | { type: 'SET_SESSIONS'; payload: SessionOverview[] | SessionTreeNode[] }
  | { type: 'SET_CURRENT_SESSION_ID'; payload: string | null }
  | { type: 'SET_SESSION_DETAIL'; payload: SessionDetail | null }
  | {
      type: 'SET_SESSION_AND_CURRENT'
      payload: { id: string | null; detail: SessionDetail | null }
    }
  | { type: 'UPDATE_SETTINGS'; payload: Partial<Settings> }
  | { type: 'SET_ROLE_OPTIONS'; payload: RoleOption[] }
  | { type: 'SET_ARCHIVED_SESSIONS'; payload: SessionOverview[] }
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
    case 'SET_ROLE_OPTIONS':
      return {
        ...state,
        roleOptions: action.payload
      }
    case 'SET_ARCHIVED_SESSIONS':
      return {
        ...state,
        archivedSessions: action.payload
      }
    case 'RESET':
      return initialState
    default:
      return state
  }
}

export type Actions = {
  setSessions: (sessions: SessionOverview[] | SessionTreeNode[]) => void
  setCurrentSessionId: (id: string | null) => void
  setSessionDetail: (detail: SessionDetail | null) => void
  selectSession: (id: string | null, detail: SessionDetail | null) => void
  updateSettings: (partial: Partial<Settings>) => void
  setRoleOptions: (roleOptions: RoleOption[]) => void
  setArchivedSessions: (sessions: SessionOverview[]) => void
  refreshSessions: (
    sessionDetail: SessionDetail | null,
    sessions?: SessionOverview[] | SessionTreeNode[]
  ) => void
  reset: () => void
}

export type UseSessionStoreReturn = {
  state: State
  actions: Actions
}

export const useSessionStore = (initial?: Partial<State>): UseSessionStoreReturn => {
  const mergedInitial: State = { ...initialState, ...(initial || {}) }
  const [state, dispatch] = useReducer(reducer, mergedInitial)

  const setSessions = useCallback((sessions: SessionOverview[] | SessionTreeNode[]) => {
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
      console.debug('[SessionStore] selectSession id:', id)
      dispatch({ type: 'SET_SESSION_AND_CURRENT', payload: { id, detail } })
    },
    []
  )

  const updateSettings = useCallback((partial: Partial<Settings>) => {
    dispatch({ type: 'UPDATE_SETTINGS', payload: partial })
  }, [])

  const setRoleOptions = useCallback((roleOptions: RoleOption[]) => {
    dispatch({ type: 'SET_ROLE_OPTIONS', payload: roleOptions })
  }, [])

  const setArchivedSessions = useCallback((sessions: SessionOverview[]) => {
    dispatch({ type: 'SET_ARCHIVED_SESSIONS', payload: sessions })
  }, [])

  const refreshSessions = useCallback(
    (
      sessionDetail: SessionDetail | null,
      sessions?: SessionOverview[] | SessionTreeNode[]
    ): void => {
      dispatch({ type: 'SET_SESSION_DETAIL', payload: sessionDetail })
      if (sessions) {
        dispatch({ type: 'SET_SESSIONS', payload: sessions })
      }
    },
    []
  )

  const reset = useCallback(() => dispatch({ type: 'RESET' }), [])

  return {
    state,
    actions: {
      setSessions,
      setCurrentSessionId,
      setSessionDetail,
      selectSession,
      updateSettings,
      setRoleOptions,
      setArchivedSessions,
      refreshSessions,
      reset
    }
  }
}
