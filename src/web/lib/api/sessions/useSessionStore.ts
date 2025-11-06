export type SessionOverview = {
  name: string
  description?: string
  updated_at: string
  created_at: string
}

export type SessionDetail = {
  id: string
  name: string
  description?: string
  updated_at: string
  created_at: string
}

export type SessionsState = {
  sessions: Array<{ id: string } & SessionOverview>
  currentSession: SessionDetail | null
  currentId: string | null
}

let sessionState: SessionsState = {
  sessions: [],
  currentSession: null,
  currentId: null,
}

/**
 * セッションの状態を設定します
 */
export const setSessionState = (state: SessionsState): void => {
  sessionState = state
}

/**
 * セッション一覧を設定します
 */
export const setSessionsList = (
  sessions: Array<{ id: string } & SessionOverview>,
): void => {
  sessionState.sessions = sessions
}

/**
 * 現在のセッション詳細を設定します
 */
export const setCurrentSession = (session: SessionDetail | null): void => {
  sessionState.currentSession = session
  if (session) {
    sessionState.currentId = session.id
  }
}

/**
 * 現在のセッションIDを設定します
 */
export const setCurrentSessionId = (id: string | null): void => {
  sessionState.currentId = id
}

/**
 * 現在のセッション状態を取得します
 */
export const getSessionState = (): SessionsState => ({
  ...sessionState,
})

/**
 * セッション状態をリセットします
 */
export const resetSessionState = (): void => {
  sessionState = {
    sessions: [],
    currentSession: null,
    currentId: null,
  }
}
