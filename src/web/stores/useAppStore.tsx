import type { JSX } from 'react'
import React, {
  createContext,
  useCallback,
  useContext,
  useMemo,
  useReducer
} from 'react'

// Types
export type ToastPosition =
  | 'top-left'
  | 'top-center'
  | 'top-right'
  | 'bottom-left'
  | 'bottom-center'
  | 'bottom-right'

export type ToastStatus = 'success' | 'failure' | 'warning'

export type ToastItem = {
  createdAt: number
  id: string
  status: ToastStatus
  description?: string
  dismissible?: boolean
  duration?: number | null
  position?: ToastPosition
  title?: string
}

type State = {
  loadingCount: number
  toasts: ToastItem[]
}

type Action =
  | { payload: ToastItem; type: 'PUSH_TOAST' }
  | { payload: { id: string }; type: 'REMOVE_TOAST' }
  | { type: 'CLEAR_TOASTS' }
  | { type: 'SHOW_LOADER' }
  | { type: 'HIDE_LOADER' }

const initialState: State = {
  toasts: [],
  loadingCount: 0
}

const reducer = (state: State, action: Action): State => {
  switch (action.type) {
    case 'PUSH_TOAST': {
      // Append newest to the end (chronological). Rendering will handle visual stacking per-position.
      return { ...state, toasts: [...state.toasts, action.payload] }
    }
    case 'REMOVE_TOAST': {
      return {
        ...state,
        toasts: state.toasts.filter((t) => t.id !== action.payload.id)
      }
    }
    case 'CLEAR_TOASTS':
      return { ...state, toasts: [] }
    case 'SHOW_LOADER':
      return { ...state, loadingCount: state.loadingCount + 1 }
    case 'HIDE_LOADER':
      return { ...state, loadingCount: Math.max(0, state.loadingCount - 1) }
    default:
      return state
  }
}

// Context value
type AppStoreContextValue = {
  isLoading: boolean
  state: State
  clearToasts: () => void
  hideLoader: () => void
  pushToast: (payload: Omit<ToastItem, 'id' | 'createdAt'>) => string
  removeToast: (id: string) => void
  showLoader: () => void
}

const AppStoreContext = createContext<AppStoreContextValue | undefined>(undefined)

let idCounter = 0
const genId = (prefix = 'toast'): string => {
  idCounter += 1

  return `${prefix}-${Date.now()}-${idCounter}`
}

export const AppStoreProvider = ({
  children
}: React.PropsWithChildren<unknown>): JSX.Element => {
  const [state, dispatch] = useReducer(reducer, initialState)

  const pushToast = useCallback((payload: Omit<ToastItem, 'id' | 'createdAt'>) => {
    const id = genId()
    const item: ToastItem = {
      id,
      createdAt: Date.now(),
      duration: 5000,
      dismissible: true,
      ...payload
    }
    dispatch({ type: 'PUSH_TOAST', payload: item })

    return id
  }, [])

  const removeToast = useCallback(
    (id: string) => dispatch({ type: 'REMOVE_TOAST', payload: { id } }),
    []
  )
  const clearToasts = useCallback(() => dispatch({ type: 'CLEAR_TOASTS' }), [])
  const showLoader = useCallback(() => dispatch({ type: 'SHOW_LOADER' }), [])
  const hideLoader = useCallback(() => dispatch({ type: 'HIDE_LOADER' }), [])

  const isLoading = useMemo(() => state.loadingCount > 0, [state.loadingCount])

  const value: AppStoreContextValue = useMemo(
    () => ({
      state,
      pushToast,
      removeToast,
      clearToasts,
      showLoader,
      hideLoader,
      isLoading
    }),
    [state, pushToast, removeToast, clearToasts, showLoader, hideLoader, isLoading]
  )

  return <AppStoreContext.Provider value={value}>{children}</AppStoreContext.Provider>
}

export const useAppStore = (): AppStoreContextValue => {
  const context = useContext(AppStoreContext)
  if (!context) throw new Error('useAppStore must be used within an AppStoreProvider')

  return context
}

// (Removed temporary default export) Use named export `useAppStore`.
