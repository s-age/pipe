# Pages Layer

## Purpose

Pages are the top-level components that represent entire routes in the application. They orchestrate data flow, manage page-specific state, and compose Organisms to create complete user interfaces.

## Responsibilities

1. **Routing** - Represent application routes (e.g., `/`, `/chat-history`)
2. **State Management** - Initialize and manage page-specific stores
3. **Data Orchestration** - Coordinate data flow between organisms
4. **Layout** - Define page-level layout and structure
5. **Store Distribution** - Pass store state and actions to organisms via Props

## Characteristics

- ✅ Can access `useAppStore` (global UI state)
- ✅ Initialize page-specific stores (e.g., `useSessionStore()`)
- ✅ Use custom hooks for handlers, actions, lifecycle
- ✅ Compose multiple Organisms
- ✅ Define page-level styles and layout
- ❌ Should NOT contain business logic (delegate to hooks)
- ❌ Should NOT have complex JSX (delegate to organisms)

## File Structure

```
pages/
└── ChatHistoryPage/
    ├── index.tsx                          # Main page component
    ├── style.css.ts                       # Page layout styles
    └── hooks/
        ├── useChatHistoryPageActions.ts   # API calls
        ├── useChatHistoryPageHandlers.ts  # Main orchestration hook
        └── useChatHistoryPageLifecycle.ts # Side effects (data loading)
```

## Template

```typescript
import type { JSX } from 'react'
import { SomeOrganism } from '@/components/organisms/SomeOrganism'
import { AnotherOrganism } from '@/components/organisms/AnotherOrganism'
import { usePage{Name}Handlers } from './hooks/usePage{Name}Handlers'
import { container, mainContent } from './style.css'

export const {Name}Page = (): JSX.Element => {
  // Initialize page store and get data/actions
  const {
    data,
    currentId,
    handleAction,
    onRefresh
  } = usePage{Name}Handlers()

  return (
    <div className={container}>
      <div className={mainContent}>
        {/* Compose organisms and pass data via Props */}
        <SomeOrganism
          data={data}
          currentId={currentId}
          onAction={handleAction}
        />

        <AnotherOrganism
          data={data}
          onRefresh={onRefresh}
        />
      </div>
    </div>
  )
}
```

## Real Example: ChatHistoryPage

```typescript
import type { JSX } from 'react'
import { ChatHistory } from '@/components/organisms/ChatHistory'
import { Header } from '@/components/organisms/Header'
import { SessionMeta } from '@/components/organisms/SessionMeta'
import { SessionTree } from '@/components/organisms/SessionTree'
import { useChatHistoryPageHandlers } from './hooks/useChatHistoryPageHandlers'
import {
  appContainer,
  mainContent,
  leftColumn,
  centerColumn,
  rightColumn
} from './style.css'

export const ChatHistoryPage = (): JSX.Element => {
  // All state management and orchestration in this hook
  const {
    sessions,
    currentSessionId,
    sessionDetail,
    expertMode,
    selectSession,
    setSessionDetail,
    onRefresh
  } = useChatHistoryPageHandlers()

  // Page only handles layout and prop distribution
  return (
    <div className={appContainer}>
      <Header />
      <div className={mainContent}>
        <div className={leftColumn}>
          <SessionTree
            sessions={sessions}
            currentSessionId={currentSessionId}
            selectSession={selectSession}
          />
        </div>

        <div className={centerColumn}>
          <ChatHistory
            sessionDetail={sessionDetail}
            currentSessionId={currentSessionId}
            expertMode={expertMode}
            setSessionDetail={setSessionDetail}
          />
        </div>

        <div className={rightColumn}>
          <SessionMeta
            key={currentSessionId}
            sessionDetail={sessionDetail}
            currentSessionId={currentSessionId}
            setSessionDetail={setSessionDetail}
            onRefresh={onRefresh}
          />
        </div>
      </div>
    </div>
  )
}
```

## Page Handlers Hook Pattern

The main orchestration hook that initializes store and composes other hooks:

```typescript
// hooks/useChatHistoryPageHandlers.ts
import { useSessionStore } from '@/stores/useChatHistoryStore'
import { useChatHistoryPageActions } from './useChatHistoryPageActions'
import { useSessionLoader } from './useChatHistoryPageLifecycle'

export const useChatHistoryPageHandlers = () => {
  // 1. Initialize page store
  const { state, actions } = useSessionStore()

  // 2. Extract state
  const {
    sessionTree: { sessions, currentSessionId },
    sessionDetail,
    settings
  } = state

  // 3. Get actions from store
  const { selectSession, setSessionDetail, refreshSessions } = actions

  // 4. Compose with Actions hook
  const { onRefresh } = useChatHistoryPageActions({
    currentSessionId,
    refreshSessions
  })

  // 5. Run lifecycle (data loading)
  useSessionLoader({ state, actions })

  // 6. Return unified interface
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

## Best Practices

### 1. Keep Pages Thin

Pages should be primarily composition - delegate logic to hooks:

```typescript
// ✅ Good - Thin page component
export const MyPage = () => {
  const { data, actions } = useMyPageHandlers()
  return <Layout><Organism {...data} {...actions} /></Layout>
}

// ❌ Bad - Fat page component
export const MyPage = () => {
  const [data, setData] = useState()
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    // 50 lines of data fetching logic
  }, [])

  const handleSubmit = async (formData) => {
    // 30 lines of business logic
  }

  // 100+ lines of JSX
  return (...)
}
```

### 2. Initialize Store Early

Always initialize page store at the top of the handlers hook:

```typescript
export const useMyPageHandlers = () => {
  // First thing - initialize store
  const { state, actions } = useMyStore()

  // Then compose with other hooks
  const { apiActions } = useMyPageActions()
  useMyPageLifecycle({ state })

  return { ...state, ...actions, ...apiActions }
}
```

### 3. Pass Minimal Props

Only pass what organisms need:

```typescript
// ✅ Good - Minimal, focused props
<SessionTree
  sessions={sessions}
  currentSessionId={currentSessionId}
  selectSession={selectSession}
/>

// ❌ Bad - Passing entire state
<SessionTree {...state} {...actions} />
```

### 4. Use Key for Dynamic Content

Reset component state when ID changes:

```typescript
<SessionMeta
  key={currentSessionId}  // Reset when session changes
  sessionDetail={sessionDetail}
  currentSessionId={currentSessionId}
/>
```

### 5. Layout Structure

Use semantic layout containers:

```typescript
<div className={appContainer}>
  <Header />
  <div className={mainContent}>
    <aside className={leftColumn}>
      <Navigation />
    </aside>
    <main className={centerColumn}>
      <PrimaryContent />
    </main>
    <aside className={rightColumn}>
      <SecondaryContent />
    </aside>
  </div>
</div>
```

## Store Management in Pages

### Global Store (useAppStore)

Pages can access global store directly but typically don't need to:

```typescript
export const MyPage = () => {
  // Usually not needed in pages - organisms use it directly
  const { pushToast, isLoading } = useAppStore()

  // More common: just pass callbacks
  const handlers = useMyPageHandlers()
  return <Organism {...handlers} />
}
```

### Page Store (useSessionStore, etc.)

Pages initialize and distribute page-specific stores:

```typescript
export const ChatHistoryPage = () => {
  // Initialize in handlers hook
  const {
    sessions,
    selectSession,
    onRefresh
  } = useChatHistoryPageHandlers()  // Store initialized here

  // Distribute via Props
  return (
    <>
      <SessionTree
        sessions={sessions}
        selectSession={selectSession}
      />
      <SessionMeta onRefresh={onRefresh} />
    </>
  )
}
```

## Testing Pages

### Integration Testing

Test pages with mocked APIs and routers:

```typescript
import { render, screen, waitFor } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import { AppStoreProvider } from '@/stores/useAppStore'
import { ChatHistoryPage } from './index'

jest.mock('@/lib/api/session/getSession')

describe('ChatHistoryPage', () => {
  it('loads and displays session data', async () => {
    const mockSession = { id: '123', purpose: 'Test' }
    mockGetSession.mockResolvedValue({ session: mockSession })

    render(
      <AppStoreProvider>
        <MemoryRouter>
          <ChatHistoryPage />
        </MemoryRouter>
      </AppStoreProvider>
    )

    await waitFor(() => {
      expect(screen.getByText('Test')).toBeInTheDocument()
    })
  })
})
```

## Common Patterns

### Loading States

```typescript
export const MyPage = () => {
  const { data, isLoading } = useMyPageHandlers()

  if (isLoading) {
    return <LoadingSpinner />
  }

  return <Content data={data} />
}
```

### Error Boundaries

```typescript
export const MyPage = () => {
  return (
    <ErrorBoundary fallback={<ErrorPage />}>
      <PageContent />
    </ErrorBoundary>
  )
}
```

### Conditional Rendering

```typescript
export const MyPage = () => {
  const { currentId, data } = useMyPageHandlers()

  return (
    <>
      <List />
      {currentId && data && (
        <Detail data={data} />
      )}
    </>
  )
}
```

## When to Split a Page

Split a page when:

- ✅ Multiple distinct routes needed
- ✅ Different layouts required
- ✅ Separate authentication requirements
- ✅ Different data loading strategies

Keep together when:

- ❌ Just different views of same data (use state instead)
- ❌ Similar layout and data requirements
- ❌ Closely related user flows

## Related Documentation

- [Components Overview](./components.md) - Architecture overview
- [Organisms](./organisms.md) - Complex sections that pages compose
- [Stores Guidelines](../stores.md) - State management patterns
- [Custom Hooks](../hooks/hooks.md) - Hook organization
