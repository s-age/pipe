# Handlers Pattern

## Purpose

Handlers hooks process UI events and coordinate between user interactions, actions (API calls), and component state. They contain the business logic for how your component responds to user input.

## Characteristics

- **Event processing** - Handles onClick, onChange, onSubmit, etc.
- **Business logic** - Validates, transforms, and orchestrates operations
- **Calls actions** - Uses Actions hooks to trigger API calls
- **State management** - May update local or global state
- **Side effects** - Can trigger navigation, show modals, etc.

## Naming Convention

```
use{ComponentName}Handlers
```

## Code Template

```typescript
import { useCallback } from 'react'
import { use{ComponentName}Actions } from './use{ComponentName}Actions'

type Use{ComponentName}HandlersProperties = {
  // Dependencies from parent component
  currentId: string | null
  onRefresh?: () => Promise<void>
  // ... other dependencies
}

export const use{ComponentName}Handlers = ({
  currentId,
  onRefresh
}: Use{ComponentName}HandlersProperties): {
  handleEvent: (event: React.SomeEvent) => Promise<void> | void
} => {
  const { actionName } = use{ComponentName}Actions()

  const handleEvent = useCallback(
    async (event: React.SomeEvent): Promise<void> => {
      // 1. Extract data from event (synchronously)
      const value = event.target.value

      // 2. Validate
      if (!currentId || !value) return

      // 3. Call action
      await actionName(currentId, { value })

      // 4. Handle success
      await onRefresh?.()
    },
    [currentId, actionName, onRefresh]
  )

  return { handleEvent }
}
```

## Real Example

```typescript
import { useCallback } from 'react'
import type { SessionDetail } from '@/lib/api/session/getSession'
import { useMultiStepReasoningActions } from './useMultiStepReasoningActions'

type UseMultiStepReasoningHandlersProperties = {
  currentSessionId: string | null
  sessionDetail: SessionDetail | null
  onRefresh: () => Promise<void>
  setSessionDetail?: (data: SessionDetail | null) => void
}

export const useMultiStepReasoningHandlers = ({
  currentSessionId,
  sessionDetail,
  onRefresh,
  setSessionDetail
}: UseMultiStepReasoningHandlersProperties): {
  handleMultiStepReasoningChange: (
    event: React.ChangeEvent<HTMLInputElement>
  ) => Promise<void>
} => {
  const { updateMultiStepReasoning } = useMultiStepReasoningActions()

  const handleMultiStepReasoningChange = useCallback(
    async (event: React.ChangeEvent<HTMLInputElement>): Promise<void> => {
      if (!currentSessionId || !sessionDetail) return

      // Read checked synchronously to avoid relying on the synthetic event
      // after an await (React may pool events).
      const checked = event.target.checked

      const result = await updateMultiStepReasoning(currentSessionId, {
        multi_step_reasoning_enabled: checked
      })

      // Update local session detail immediately from the API response so the UI
      // reflects the change without waiting for a full sessions refresh.
      if (setSessionDetail) {
        setSessionDetail(result.session)
      }

      // Refresh the full session list in the background
      await onRefresh()
    },
    [
      currentSessionId,
      sessionDetail,
      updateMultiStepReasoning,
      onRefresh,
      setSessionDetail
    ]
  )

  return { handleMultiStepReasoningChange }
}
```

## Usage in Components

```typescript
import { useMultiStepReasoningHandlers } from './hooks/useMultiStepReasoningHandlers'

const SessionMetaBasic = ({ sessionId, sessionDetail, onRefresh }) => {
  const { handleMultiStepReasoningChange } = useMultiStepReasoningHandlers({
    currentSessionId: sessionId,
    sessionDetail,
    onRefresh,
    setSessionDetail: undefined
  })

  return (
    <input
      type="checkbox"
      checked={sessionDetail?.multi_step_reasoning_enabled}
      onChange={handleMultiStepReasoningChange}
    />
  )
}
```

## Handler Patterns

### Simple Event Handler

```typescript
const handleClick = useCallback(() => {
  onSelect?.(value)
}, [onSelect, value])
```

### Form Submit Handler

```typescript
const handleSubmit = useCallback(
  async (event: React.FormEvent) => {
    event.preventDefault()

    await createSession(formData)
    navigate('/sessions')
  },
  [formData, createSession, navigate]
)
```

### Keyboard Event Handler

```typescript
const handleKeyDown = useCallback(
  (event: React.KeyboardEvent) => {
    if (event.key === 'Enter' && !event.shiftKey) {
      event.preventDefault()
      handleSubmit()
    }
  },
  [handleSubmit]
)
```

### State Update Handler

```typescript
const handleChange = useCallback(
  (event: React.ChangeEvent<HTMLInputElement>) => {
    const newValue = event.target.value
    setValue(newValue)
    onChange?.(newValue)
  },
  [onChange]
)
```

## When to Use Handlers

✅ **Use Handlers when:**

- Processing user events (click, change, submit, keydown)
- Orchestrating multiple actions
- Need to validate before calling actions
- Managing component-specific business logic
- Coordinating state updates and API calls

❌ **Don't use Handlers for:**

- Pure API calls (use Actions)
- Side effects with useEffect (use Lifecycle)
- Only passing through to parent callbacks (call directly)

## Event Handler Best Practices

### 1. Extract Event Data Synchronously

React may pool synthetic events, so extract data before `await`:

```typescript
// ✅ Good
const handleChange = async (event: React.ChangeEvent<HTMLInputElement>) => {
  const checked = event.target.checked // Extract before await
  await updateSetting(checked)
}

// ❌ Bad
const handleChange = async (event: React.ChangeEvent<HTMLInputElement>) => {
  await updateSetting(event.target.checked) // Event may be pooled
}
```

### 2. Early Return for Validation

```typescript
const handleSubmit = useCallback(async () => {
  if (!sessionId || !isValid) return // Guard clauses first

  await submitForm()
}, [sessionId, isValid, submitForm])
```

### 3. Prevent Default When Needed

```typescript
const handleSubmit = useCallback((event: React.FormEvent) => {
  event.preventDefault() // Prevent form submission
  // ... handle submit
}, [])
```

### 4. Use Optional Chaining for Callbacks

```typescript
const handleComplete = useCallback(() => {
  onComplete?.() // Safe even if onComplete is undefined
}, [onComplete])
```

## Composing Handlers

Handlers can compose multiple actions:

```typescript
export const useFormHandlers = ({ sessionId, onSuccess }) => {
  const { updateSession } = useSessionActions()
  const { createReference } = useReferenceActions()
  const { showSuccess } = useToast()

  const handleSubmit = useCallback(
    async (formData) => {
      // Call multiple actions in sequence
      await updateSession(sessionId, formData.session)
      await createReference(sessionId, formData.reference)

      onSuccess?.()
    },
    [sessionId, updateSession, createReference, showSuccess, onSuccess]
  )

  return { handleSubmit }
}
```

## Testing Handlers

```typescript
import { renderHook, act } from '@testing-library/react'
import { useMultiStepReasoningHandlers } from './useMultiStepReasoningHandlers'

jest.mock('./useMultiStepReasoningActions')

describe('useMultiStepReasoningHandlers', () => {
  it('updates multi-step reasoning on checkbox change', async () => {
    const mockRefresh = jest.fn()
    const mockUpdate = jest.fn()

    const { result } = renderHook(() =>
      useMultiStepReasoningHandlers({
        currentSessionId: 'session-123',
        sessionDetail: mockSession,
        onRefresh: mockRefresh
      })
    )

    const mockEvent = {
      target: { checked: true }
    } as React.ChangeEvent<HTMLInputElement>

    await act(async () => {
      await result.current.handleMultiStepReasoningChange(mockEvent)
    })

    expect(mockUpdate).toHaveBeenCalledWith('session-123', {
      multi_step_reasoning_enabled: true
    })
    expect(mockRefresh).toHaveBeenCalled()
  })
})
```

## Related Patterns

- [Actions](./useActions.md) - Handlers consume actions to trigger API calls
- [Lifecycle](./useLifecycle.md) - May trigger handlers on mount or interval

## Error Handling Responsibility

Handlers hooks are **not** responsible for error handling or user feedback, including toast notifications. Actions hooks are solely responsible for handling errors and performing UI notifications.

- Actions hooks handle errors and show toast notifications.
- Handlers hooks should call Actions without their own `try-catch` blocks for API calls.

---
