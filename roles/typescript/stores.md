# Stores Guidelines

## Overview

Stores in this project manage page-specific state using React's `useReducer` pattern. They are located in `src/web/stores/` and follow strict access rules to maintain a clear component hierarchy.

## Core Principles

1. **Page ownership** - Stores are managed by pages (`components/pages`)
2. **Limited access** - Only pages and organisms can directly access stores
3. **No molecules/atoms** - Lower-level components receive props from parents
4. **useReducer pattern** - All stores use reducer pattern for predictable state updates

## Store Types

### 1. useAppStore - Global Application State

**Purpose:** Manages application-wide concerns like loading indicators, toast notifications, and modals.

**Location:** `src/web/stores/useAppStore.tsx`

**Responsibilities:**

- Toast notifications (success, failure, warning)
- Loading state (global loader)
- Modal state (future)

**Pattern:** Context Provider with useReducer

```typescript
import { useAppStore } from '@/stores/useAppStore'

// In any organism or page
const MyComponent = () => {
  const { pushToast, isLoading, showLoader, hideLoader } = useAppStore()

  // Show loading indicator
  showLoader()
  // ... async operation
  hideLoader()

  // Show toast notification
  pushToast({
    status: 'success',
    title: 'Success',
    description: 'Operation completed'
  })
}
```

### 2. Page Stores - Page-Specific State

**Purpose:** Manages state specific to a single page.

**Location:** `src/web/stores/use{PageName}Store.ts`

**Pattern:** Custom hook with useReducer (no Context)

```typescript
import { useSessionStore } from '@/stores/useChatHistoryStore'

// In ChatHistoryPage
const ChatHistoryPage = () => {
  const { state, actions } = useSessionStore()

  // Access state
  const { sessionTree, sessionDetail, settings } = state

  // Dispatch actions
  actions.selectSession(sessionId, detail)
  actions.setSessions(sessions)
}
```

## Access Rules

### ✅ Allowed Access

**Pages (`components/pages/*`):**

- Can create and manage stores
- Can pass store state/actions to child organisms
- Responsible for store lifecycle

**Organisms (`components/organisms/*`):**

- Can access `useAppStore` directly (toast, loading)
- Can receive page store state/actions via props
- Should NOT create page stores

### ❌ Forbidden Access

**Molecules (`components/molecules/*`):**

- Cannot access stores directly
- Must receive all data via props

**Atoms (`components/atoms/*`):**

- Cannot access stores directly
- Must receive all data via props

## Store Structure

### useAppStore (Context Provider)

```typescript
// State
type State = {
  toasts: ToastItem[]
  loadingCount: number
}

// Actions
type Action =
  | { type: 'PUSH_TOAST'; payload: ToastItem }
  | { type: 'REMOVE_TOAST'; payload: { id: string } }
  | { type: 'SHOW_LOADER' }
  | { type: 'HIDE_LOADER' }

// Provider
export const AppStoreProvider = ({ children }) => {
  const [state, dispatch] = useReducer(reducer, initialState)

  // Wrapped actions
  const pushToast = useCallback((payload) => {
    dispatch({ type: 'PUSH_TOAST', payload: { ...payload, id: genId() } })
  }, [])

  return (
    <AppStoreContext.Provider value={{ state, pushToast, ... }}>
      {children}
    </AppStoreContext.Provider>
  )
}

// Consumer hook
export const useAppStore = () => {
  const context = useContext(AppStoreContext)
  if (!context) throw new Error('useAppStore must be used within AppStoreProvider')
  return context
}
```

### Page Store (Custom Hook)

```typescript
// State
export type State = {
  sessionTree: SessionTree
  sessionDetail: SessionDetail | null
  settings: Settings
}

// Actions
export type Action =
  | { type: 'SET_SESSIONS'; payload: SessionOverview[] }
  | { type: 'SET_CURRENT_SESSION_ID'; payload: string | null }
  | { type: 'SET_SESSION_DETAIL'; payload: SessionDetail | null }
  | { type: 'UPDATE_SETTINGS'; payload: Partial<Settings> }
  | { type: 'RESET' }

// Reducer
export const reducer = (state: State, action: Action): State => {
  switch (action.type) {
    case 'SET_SESSIONS':
      return { ...state, sessionTree: { ...state.sessionTree, sessions: action.payload } }
    // ... other cases
    default:
      return state
  }
}

// Actions interface
export type Actions = {
  setSessions: (sessions: SessionOverview[]) => void
  setCurrentSessionId: (id: string | null) => void
  setSessionDetail: (detail: SessionDetail | null) => void
  updateSettings: (partial: Partial<Settings>) => void
  reset: () => void
}

// Store hook
export const useSessionStore = (initial?: Partial<State>) => {
  const [state, dispatch] = useReducer(reducer, { ...initialState, ...initial })

  const setSessions = useCallback((sessions: SessionOverview[]) => {
    dispatch({ type: 'SET_SESSIONS', payload: sessions })
  }, [])

  // ... other actions

  return {
    state,
    actions: { setSessions, setCurrentSessionId, ... }
  }
}
```

## Complete Examples

### Using useAppStore in Organisms

```typescript
// src/web/components/organisms/Toast/hooks/useToastActions.tsx
import { useCallback } from 'react'
import { useAppStore } from '@/stores/useAppStore'
import type { ToastStatus, ToastPosition } from '@/stores/useAppStore'

export const useToastActions = () => {
  const { pushToast } = useAppStore()

  const show = useCallback(
    (
      status: ToastStatus,
      title?: string,
      description?: string,
      position?: ToastPosition
    ) => {
      return pushToast({ status, title, description, position })
    },
    [pushToast]
  )

  const success = useCallback(
    (description: string, title = 'Success') => {
      return show('success', title, description)
    },
    [show]
  )

  const failure = useCallback(
    (description: string, title = 'Error') => {
      return show('failure', title, description)
    },
    [show]
  )

  return { show, success, failure }
}
```

### Using Page Store in Pages

```typescript
// src/web/components/pages/ChatHistoryPage/hooks/useChatHistoryPageHandlers.ts
import { useSessionStore } from '@/stores/useChatHistoryStore'
import { useChatHistoryPageActions } from './useChatHistoryPageActions'
import { useSessionLoader } from './useChatHistoryPageLifecycle'

export const useChatHistoryPageHandlers = () => {
  // Initialize store
  const { state, actions } = useSessionStore()

  // Extract state
  const {
    sessionTree: { sessions, currentSessionId },
    sessionDetail,
    settings
  } = state

  // Use actions
  const { selectSession, setSessionDetail, refreshSessions } = actions

  // Compose with other hooks
  const { onRefresh } = useChatHistoryPageActions({ currentSessionId, refreshSessions })
  useSessionLoader({ state, actions })

  // Return combined interface
  return {
    sessions,
    currentSessionId,
    sessionDetail,
    expertMode: settings.expertMode ?? true,
    selectSession,
    setSessionDetail,
    onRefresh
  }
}
```

### Passing Store Data to Organisms

```typescript
// src/web/components/pages/ChatHistoryPage/index.tsx
import { ChatHistory } from '@/components/organisms/ChatHistory'
import { SessionMeta } from '@/components/organisms/SessionMeta'
import { useChatHistoryPageHandlers } from './hooks/useChatHistoryPageHandlers'

export const ChatHistoryPage = () => {
  // Store managed in page handlers
  const {
    sessions,
    currentSessionId,
    sessionDetail,
    selectSession,
    setSessionDetail,
    onRefresh
  } = useChatHistoryPageHandlers()

  return (
    <div>
      {/* Pass store data as props to organisms */}
      <SessionTree
        sessions={sessions}
        currentSessionId={currentSessionId}
        selectSession={selectSession}
      />

      <ChatHistory
        sessionId={currentSessionId}
        sessionDetail={sessionDetail}
        onRefresh={onRefresh}
      />

      <SessionMeta
        sessionId={currentSessionId}
        sessionDetail={sessionDetail}
        setSessionDetail={setSessionDetail}
        onRefresh={onRefresh}
      />
    </div>
  )
}
```

## When to Create a New Store

### Create a Page Store when:

✅ You have page-specific state that needs to be shared across multiple organisms
✅ The state is complex enough to benefit from reducer pattern
✅ Multiple organisms need to coordinate around the same state
✅ You want predictable state updates with actions

### Use useAppStore when:

✅ Showing toast notifications
✅ Managing loading indicators
✅ Global modal state
✅ Any application-wide UI state

### Use local state when:

✅ State is only used within one component
✅ Simple toggle or input state
✅ No need to share with siblings
✅ Component-specific UI state (hover, focus, etc.)

## Naming Conventions

**Store files:**

- Global: `useAppStore.tsx` (with Provider)
- Page: `use{PageName}Store.ts`

**Example:**

- `useAppStore.tsx` - Global app state
- `useChatHistoryStore.ts` - ChatHistoryPage state
- `useStartSessionStore.ts` - StartSessionPage state (if needed)

## State Structure Best Practices

### 1. Group Related State

```typescript
// ✅ Good - grouped by domain
type State = {
  sessionTree: {
    sessions: SessionOverview[]
    currentSessionId: string | null
  }
  sessionDetail: SessionDetail | null
  settings: Settings
}

// ❌ Bad - flat structure
type State = {
  sessions: SessionOverview[]
  currentSessionId: string | null
  sessionDetail: SessionDetail | null
  temperature: number
  topP: number
}
```

### 2. Use Discriminated Unions for Actions

```typescript
// ✅ Good - type-safe actions
type Action =
  | { type: 'SET_SESSIONS'; payload: SessionOverview[] }
  | { type: 'SET_CURRENT_SESSION_ID'; payload: string | null }
  | { type: 'RESET' }

// ❌ Bad - loose typing
type Action = {
  type: string
  payload?: any
}
```

### 3. Export Types for Consumers

```typescript
// Export state and actions types
export type State = { ... }
export type Actions = { ... }

// Consumers can import types
import type { State, Actions } from '@/stores/useSessionStore'
```

### 4. Provide Initial State

```typescript
export const initialState: State = {
  sessionTree: { sessions: [], currentSessionId: null },
  sessionDetail: null,
  settings: { parameters: { temperature: null, top_p: null, top_k: null } }
}

// Allow overriding initial state
export const useSessionStore = (initial?: Partial<State>) => {
  const mergedInitial = { ...initialState, ...initial }
  const [state, dispatch] = useReducer(reducer, mergedInitial)
  // ...
}
```

## Testing Stores

### Testing useAppStore

```typescript
import { renderHook, act } from '@testing-library/react'
import { AppStoreProvider, useAppStore } from './useAppStore'

const wrapper = ({ children }) => <AppStoreProvider>{children}</AppStoreProvider>

describe('useAppStore', () => {
  it('shows and hides loader', () => {
    const { result } = renderHook(() => useAppStore(), { wrapper })

    expect(result.current.isLoading).toBe(false)

    act(() => {
      result.current.showLoader()
    })

    expect(result.current.isLoading).toBe(true)

    act(() => {
      result.current.hideLoader()
    })

    expect(result.current.isLoading).toBe(false)
  })
})
```

### Testing Page Stores

```typescript
import { renderHook, act } from '@testing-library/react'
import { useSessionStore } from './useChatHistoryStore'

describe('useSessionStore', () => {
  it('sets sessions', () => {
    const { result } = renderHook(() => useSessionStore())

    const mockSessions = [{ id: '1', purpose: 'Test' }]

    act(() => {
      result.current.actions.setSessions(mockSessions)
    })

    expect(result.current.state.sessionTree.sessions).toEqual(mockSessions)
  })
})
```

## Common Patterns

### Loading Wrapper

```typescript
const loadWithLoading = async <T>(operation: () => Promise<T>): Promise<T> => {
  const { showLoader, hideLoader } = useAppStore()

  showLoader()
  try {
    return await operation()
  } finally {
    hideLoader()
  }
}
```

### Toast Notification Helper

```typescript
// In Actions hook
const { pushToast } = useAppStore()

const updateSession = useCallback(
  async (id: string, data: UpdateData) => {
    try {
      const result = await editSession(id, data)
      pushToast({
        status: 'success',
        title: 'Updated',
        description: result.message
      })
      return result
    } catch (error) {
      pushToast({
        status: 'failure',
        title: 'Error',
        description: (error as Error).message
      })
      throw error
    }
  },
  [pushToast]
)
```

### Composite Actions

```typescript
// Store action that updates multiple pieces of state
const selectSession = useCallback(
  (id: string | null, detail: SessionDetail | null) => {
    dispatch({
      type: 'SET_SESSION_AND_CURRENT',
      payload: { id, detail }
    })
  },
  []
)

// In reducer
case 'SET_SESSION_AND_CURRENT':
  return {
    ...state,
    sessionTree: { ...state.sessionTree, currentSessionId: action.payload.id },
    sessionDetail: action.payload.detail
  }
```

## Migration Guide

### From useState to Store

When component state grows complex, migrate to a store:

```typescript
// Before - multiple useState
const [sessions, setSessions] = useState([])
const [currentId, setCurrentId] = useState(null)
const [detail, setDetail] = useState(null)

// After - single store
const { state, actions } = useSessionStore()
const { sessions, currentSessionId, sessionDetail } = state
```

### Adding Store to Existing Page

1. Create store file in `src/web/stores/`
2. Define State, Action, reducer
3. Create custom hook with actions
4. Use in page handlers hook
5. Pass to organisms via props

## Related Documentation

- [Custom Hooks Guidelines](./hooks/hooks.md) - How stores integrate with hooks
- [Handlers Pattern](./hooks/useHandlers.md) - Using store actions in handlers
- [Components Guidelines](./components/organisms.md) - Component hierarchy
