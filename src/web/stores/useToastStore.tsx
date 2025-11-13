import type { JSX } from 'react'
import React, { createContext, useCallback, useContext, useReducer } from 'react'

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
  id: string
  status: ToastStatus
  position?: ToastPosition
  title?: string
  description?: string
  duration?: number | null
  dismissible?: boolean
  createdAt: number
}

type State = {
  toasts: ToastItem[]
}

type Action =
  | { type: 'PUSH_TOAST'; payload: ToastItem }
  | { type: 'REMOVE_TOAST'; payload: { id: string } }
  | { type: 'CLEAR_TOASTS' }

const initialState: State = {
  toasts: []
}

const reducer = (state: State, action: Action): State => {
  switch (action.type) {
    case 'PUSH_TOAST': {
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
    default:
      return state
  }
}

type ToastStoreContextValue = {
  toasts: ToastItem[]
  pushToast: (payload: Omit<ToastItem, 'id' | 'createdAt'>) => string
  removeToast: (id: string) => void
  clearToasts: () => void
}

const ToastStoreContext = createContext<ToastStoreContextValue | undefined>(undefined)

let idCounter = 0
const genId = (prefix = 'toast'): string => {
  idCounter += 1

  return `${prefix}-${Date.now()}-${idCounter}`
}

export const ToastStoreProvider = ({
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

  // Don't memoize value - toast updates should only affect Toast component
  const value: ToastStoreContextValue = {
    toasts: state.toasts,
    pushToast,
    removeToast,
    clearToasts
  }

  return (
    <ToastStoreContext.Provider value={value}>{children}</ToastStoreContext.Provider>
  )
}

export const useToastStore = (): ToastStoreContextValue => {
  const context = useContext(ToastStoreContext)
  if (!context)
    throw new Error('useToastStore must be used within a ToastStoreProvider')

  return context
}
