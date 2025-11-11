# Organisms Layer

## Purpose

Organisms are complex, self-contained sections of the UI that combine multiple Molecules and Atoms to create functional features. They handle business logic, data integration, and user interactions.

## Responsibilities

1. **Feature Implementation** - Complete functional sections (forms, lists, headers)
2. **Business Logic** - Handle domain-specific operations via custom hooks
3. **Data Integration** - Consume APIs, manage local state, coordinate updates
4. **Composition** - Combine Molecules and Atoms into cohesive units
5. **User Interactions** - Respond to user events and update state

## Characteristics

- ✅ Can access `useAppStore` directly (toast, loading)
- ✅ Receive page store data via Props
- ✅ Use custom hooks for Actions/Handlers/Lifecycle
- ✅ Compose Molecules and Atoms
- ✅ Manage local UI state (form state, expanded/collapsed)
- ❌ Should NOT access page stores directly (use Props)
- ❌ Should NOT handle routing (Pages responsibility)

## File Structure

```
organisms/
└── SessionMeta/
    ├── index.tsx                        # Main organism component
    ├── style.css.ts                     # Component styles
    └── hooks/
        ├── useSessionMetaActions.ts     # API calls
        ├── useSessionMetaHandlers.ts    # Event handlers
        └── useSessionMetaLifecycle.ts   # Side effects (optional)
```

## Template

```typescript
import type { JSX } from 'react'
import { SomeMolecule } from '@/components/molecules/SomeMolecule'
import { SomeAtom } from '@/components/atoms/SomeAtom'
import { use{Name}Handlers } from './hooks/use{Name}Handlers'
import { container, section } from './style.css'

type {Name}Properties = {
  data: DataType
  onAction: (params: ActionParams) => void | Promise<void>
}

export const {Name} = ({
  data,
  onAction
}: {Name}Properties): JSX.Element => {
  // Use custom hooks for logic
  const { localState, handleEvent } = use{Name}Handlers({ data, onAction })

  return (
    <div className={container}>
      {/* Compose molecules and atoms */}
      <SomeMolecule
        value={localState.value}
        onChange={handleEvent}
      />

      <SomeAtom onClick={handleEvent}>
        Submit
      </SomeAtom>
    </div>
  )
}
```

## Real Example: SessionMeta

```typescript
import type { JSX } from 'react'
import React from 'react'
import { Button } from '@/components/atoms/Button'
import { Form, useFormContext } from '@/components/organisms/Form'
import { HyperParameters } from '@/components/organisms/HyperParameters'
import { ReferenceList } from '@/components/organisms/ReferenceList'
import { SessionMetaBasic } from '@/components/organisms/SessionMetaBasic'
import { TodoList } from '@/components/organisms/TodoList'
import { useSessionMetaHandlers } from './hooks/useSessionMetaHandlers'
import type { SessionDetail } from '@/lib/api/session/getSession'
import { metaColumn, sessionMetaSection } from './style.css'

type SessionMetaProperties = {
  sessionDetail: SessionDetail | null
  currentSessionId: string | null
  setSessionDetail: (data: SessionDetail | null) => void
  onRefresh: () => Promise<void>
}

export const SessionMeta = ({
  sessionDetail,
  currentSessionId,
  setSessionDetail,
  onRefresh
}: SessionMetaProperties): JSX.Element | null => {
  // Delegate logic to handlers hook
  const { defaultValues, onSubmit, isSubmitting, saved } = useSessionMetaHandlers({
    sessionDetail,
    currentSessionId,
    onRefresh
  })

  if (sessionDetail === null) {
    return null
  }

  const MetaContent = (): JSX.Element => {
    const { handleSubmit } = useFormContext()

    const handleSaveClick = React.useCallback((): void => {
      void handleSubmit(onSubmit)()
    }, [handleSubmit])

    return (
      <>
        <div className={sessionMetaSection}>
          <SessionMetaBasic
            sessionDetail={sessionDetail}
            currentSessionId={currentSessionId}
            setSessionDetail={setSessionDetail}
            onRefresh={onRefresh}
          />
        </div>

        <div className={sessionMetaSection}>
          <HyperParameters
            sessionDetail={sessionDetail}
            currentSessionId={currentSessionId}
            onRefresh={onRefresh}
          />
        </div>

        <div className={sessionMetaSection}>
          <ReferenceList
            sessionId={currentSessionId}
            references={sessionDetail.references}
            onRefresh={onRefresh}
          />
        </div>

        <div className={sessionMetaSection}>
          <TodoList
            sessionId={currentSessionId}
            todos={sessionDetail.todos}
            onRefresh={onRefresh}
          />
        </div>

        <Button onClick={handleSaveClick} disabled={isSubmitting}>
          {saved ? '✓ Saved' : 'Save Meta'}
        </Button>
      </>
    )
  }

  return (
    <div className={metaColumn}>
      <Form defaultValues={defaultValues}>
        <MetaContent />
      </Form>
    </div>
  )
}
```

## Access Patterns

### ✅ Accessing useAppStore

Organisms can directly access global UI state:

```typescript
import { useAppStore } from '@/stores/useAppStore'

export const MyOrganism = ({ data }) => {
  const { pushToast, isLoading } = useAppStore()

  const handleAction = async () => {
    try {
      await someApiCall()
      pushToast({ status: 'success', title: 'Success!' })
    } catch (error) {
      pushToast({ status: 'failure', title: 'Error' })
    }
  }

  return <div>...</div>
}
```

### ✅ Receiving Page Store via Props

Organisms receive page-specific state through Props:

```typescript
type SessionTreeProperties = {
  sessions: SessionOverview[]        // From page store
  currentSessionId: string | null    // From page store
  selectSession: (id: string) => void // Page store action
}

export const SessionTree = ({
  sessions,
  currentSessionId,
  selectSession
}: SessionTreeProperties) => {
  // Use Props, don't access useSessionStore directly
  return (
    <ul>
      {sessions.map(session => (
        <li
          key={session.id}
          onClick={() => selectSession(session.id)}
          className={session.id === currentSessionId ? 'active' : ''}
        >
          {session.purpose}
        </li>
      ))}
    </ul>
  )
}
```

## Custom Hooks Pattern

### Actions Hook

API calls with error handling:

```typescript
// hooks/useSessionMetaActions.ts
import { useCallback } from 'react'
import { useToast } from '@/components/organisms/Toast/hooks/useToast'
import { editSessionMeta } from '@/lib/api/session/editSessionMeta'

export const useSessionMetaActions = () => {
  const toast = useToast()

  const updateSessionMeta = useCallback(
    async (sessionId: string, data: EditSessionMetaRequest) => {
      try {
        const result = await editSessionMeta(sessionId, data)
        toast.success(result?.message || 'Session updated')
        return result
      } catch (error: unknown) {
        toast.failure((error as Error).message)
        throw error
      }
    },
    [toast]
  )

  return { updateSessionMeta }
}
```

### Handlers Hook

Main orchestration hook:

```typescript
// hooks/useSessionMetaHandlers.ts
import { useState, useCallback } from 'react'
import { useSessionMetaActions } from './useSessionMetaActions'

export const useSessionMetaHandlers = ({
  sessionDetail,
  currentSessionId,
  onRefresh
}) => {
  const [isSubmitting, setIsSubmitting] = useState(false)
  const { updateSessionMeta } = useSessionMetaActions()

  const onSubmit = useCallback(
    async (formData) => {
      if (!currentSessionId) return

      setIsSubmitting(true)
      try {
        await updateSessionMeta(currentSessionId, formData)
        await onRefresh()
      } finally {
        setIsSubmitting(false)
      }
    },
    [currentSessionId, updateSessionMeta, onRefresh]
  )

  return {
    defaultValues: sessionDetail,
    onSubmit,
    isSubmitting
  }
}
```

## Best Practices

### 1. Accept Focused Props

Only accept what you need:

```typescript
// ✅ Good - Focused props
type Props = {
  sessionId: string
  references: Reference[]
  onRefresh: () => Promise<void>
}

// ❌ Bad - Accepting entire store
type Props = {
  state: State
  actions: Actions
}
```

### 2. Delegate Logic to Hooks

Keep component focused on rendering:

```typescript
// ✅ Good - Logic in hooks
export const MyOrganism = (props) => {
  const { data, handlers } = useMyOrganismHandlers(props)
  return <div>...</div>
}

// ❌ Bad - Logic inline
export const MyOrganism = (props) => {
  const [state, setState] = useState()
  useEffect(() => {
    // 50 lines of logic
  }, [])
  const handleSubmit = async () => {
    // 30 lines of logic
  }
  return <div>...</div>
}
```

### 3. Use Form Context for Form Organisms

```typescript
import { Form, useFormContext } from '@/components/organisms/Form'

export const FormOrganism = ({ defaultValues, onSubmit }) => {
  return (
    <Form defaultValues={defaultValues}>
      <FormContent onSubmit={onSubmit} />
    </Form>
  )
}

const FormContent = ({ onSubmit }) => {
  const { handleSubmit, formState } = useFormContext()

  return (
    <form onSubmit={handleSubmit(onSubmit)}>
      {/* Form fields */}
    </form>
  )
}
```

### 4. Handle Loading States

```typescript
export const DataOrganism = ({ data }) => {
  const { isLoading } = useAppStore()

  if (isLoading) {
    return <LoadingSpinner />
  }

  if (!data) {
    return <EmptyState />
  }

  return <Content data={data} />
}
```

### 5. Compose Child Organisms

Organisms can contain other organisms:

```typescript
export const ParentOrganism = (props) => {
  return (
    <div>
      <ChildOrganism1 {...props} />
      <ChildOrganism2 {...props} />
    </div>
  )
}
```

## Common Patterns

### List Organism

```typescript
export const TodoList = ({ sessionId, todos, onRefresh }) => {
  const { deleteTodo } = useTodoActions()

  const handleDelete = async (todoId: string) => {
    await deleteTodo(sessionId, todoId)
    await onRefresh()
  }

  return (
    <ul>
      {todos.map(todo => (
        <TodoItem
          key={todo.id}
          todo={todo}
          onDelete={() => handleDelete(todo.id)}
        />
      ))}
    </ul>
  )
}
```

### Form Organism

```typescript
export const StartSessionForm = ({ onSubmit }) => {
  const { defaultValues } = useStartSessionFormHandlers()

  return (
    <Form defaultValues={defaultValues}>
      <InputField name="purpose" label="Purpose" />
      <TextareaField name="background" label="Background" />
      <Button type="submit" onClick={handleSubmit(onSubmit)}>
        Start
      </Button>
    </Form>
  )
}
```

### Toggle Organism

```typescript
export const CollapsibleSection = ({ title, children }) => {
  const [isOpen, setIsOpen] = useState(false)

  return (
    <div>
      <button onClick={() => setIsOpen(!isOpen)}>
        {title} {isOpen ? '▼' : '▶'}
      </button>
      {isOpen && <div>{children}</div>}
    </div>
  )
}
```

## Testing Organisms

### Component Tests

```typescript
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import { AppStoreProvider } from '@/stores/useAppStore'
import { SessionMeta } from './index'

jest.mock('./hooks/useSessionMetaHandlers')

describe('SessionMeta', () => {
  it('submits form data', async () => {
    const mockOnSubmit = jest.fn()
    mockUseSessionMetaHandlers.mockReturnValue({
      defaultValues: {},
      onSubmit: mockOnSubmit,
      isSubmitting: false
    })

    render(
      <AppStoreProvider>
        <SessionMeta
          sessionDetail={mockSession}
          currentSessionId="123"
          onRefresh={jest.fn()}
        />
      </AppStoreProvider>
    )

    const saveButton = screen.getByText('Save Meta')
    fireEvent.click(saveButton)

    await waitFor(() => {
      expect(mockOnSubmit).toHaveBeenCalled()
    })
  })
})
```

## When to Create an Organism

Create an organism when:

- ✅ Feature requires multiple molecules/atoms
- ✅ Has business logic or API integration
- ✅ Represents a complete functional section
- ✅ Needs to be reused across pages

Use a molecule instead when:

- ❌ Just combining 2-3 atoms without logic
- ❌ Pure UI component without business logic
- ❌ No API calls or complex state

## Related Documentation

- [Components Overview](./components.md) - Architecture overview
- [Pages](./pages.md) - How pages compose organisms
- [Molecules](./molecules.md) - Building blocks of organisms
- [Custom Hooks](../hooks/hooks.md) - Hook patterns
- [Stores](../stores.md) - State management access
