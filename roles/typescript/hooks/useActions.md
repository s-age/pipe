# Actions Pattern

## Purpose

Actions hooks orchestrate API calls, providing a consistent interface for data operations. They manage error handling, display toast notifications, and return promises for asynchronous processes, potentially combining multiple API interactions.

## Characteristics

- **Integrated Error & UI Feedback** - Handles errors and displays toast notifications for user feedback.
- **Asynchronous Orchestration** - Returns promises for managing complex asynchronous flows, including multiple API calls.
- **Stateless** - Does not manage component state
- **Reusable** - Can be used by multiple components

## Naming Convention

```
use{ComponentName}Actions
```

## Code Template

```typescript
import { useCallback } from 'react'
import { useToast } from '@/components/organisms/Toast/hooks/useToast'
import { apiFunction } from '@/lib/api/...'
import type { ApiRequest, ApiResponse } from '@/lib/api/...'

export const use{ComponentName}Actions = (): {
  actionName: (id: string, payload: ApiRequest) => Promise<ApiResponse>
} => {
  const toast = useToast()

  const actionName = useCallback(
    async (id: string, payload: ApiRequest): Promise<ApiResponse> => {
      try {
        const result = await apiFunction(id, payload)
        toast.success(result?.message || 'Operation successful')
        return result
      } catch (error: unknown) {
        toast.failure((error as Error).message || 'Operation failed')
        throw error
      }
    },
    [toast]
  )

  return { actionName }
}
```

## Real Example

```typescript
import { useCallback } from 'react'
import { useToast } from '@/components/organisms/Toast/hooks/useToast'
import { editMultiStepReasoning } from '@/lib/api/session/editMultiStepReasoning'
import type { EditMultiStepReasoningRequest } from '@/lib/api/session/editMultiStepReasoning'
import type { SessionDetail } from '@/lib/api/session/getSession'

export const useMultiStepReasoningActions = (): {
  updateMultiStepReasoning: (
    sessionId: string,
    payload: EditMultiStepReasoningRequest
  ) => Promise<{ message: string; session: SessionDetail }>
} => {
  const toast = useToast()

  const updateMultiStepReasoning = useCallback(
    async (sessionId: string, payload: EditMultiStepReasoningRequest) => {
      try {
        const result = await editMultiStepReasoning(sessionId, payload)
        toast.success(result?.message || 'Multi-step reasoning updated')
        return result
      } catch (error: unknown) {
        toast.failure(
          (error as Error).message || 'Failed to update multi-step reasoning'
        )
        throw error
      }
    },
    [toast]
  )

  return { updateMultiStepReasoning }
}
```

## Usage in Components

```typescript
// In a Handlers hook
import { useMultiStepReasoningActions } from './useMultiStepReasoningActions'

export const useMultiStepReasoningHandlers = ({ sessionId, onRefresh }) => {
  const { updateMultiStepReasoning } = useMultiStepReasoningActions()

  const handleChange = useCallback(
    async (event: React.ChangeEvent<HTMLInputElement>) => {
      const checked = event.target.checked
      await updateMultiStepReasoning(sessionId, {
        multi_step_reasoning_enabled: checked
      })
      await onRefresh()
    },
    [sessionId, updateMultiStepReasoning, onRefresh]
  )

  return { handleChange }
}
```

## When to Use Actions

✅ **Use Actions when:**

- Wrapping API calls (CRUD operations)
- Need consistent error handling
- Want to show toast notifications
- Multiple components need the same API call
- Need to orchestrate multiple API calls and manage their combined outcome.

❌ **Don't use Actions for:**

- UI state management (use Handlers)
- Side effects with useEffect (use Lifecycle)
- Complex business logic (consider a separate service)

## Best Practices

1. **One action per API endpoint** - Keep actions focused
2. **Always use useCallback** - Prevent unnecessary re-renders
3. **Include toast notifications** - Provide user feedback
4. **Type everything** - Use proper TypeScript types for requests/responses
5. **Throw errors** - Let handlers decide how to handle failures
6. **Return API responses** - Don't transform data in actions



## Testing Actions

```typescript
import { renderHook, act } from '@testing-library/react'
import { useMultiStepReasoningActions } from './useMultiStepReasoningActions'

jest.mock('@/lib/api/session/editMultiStepReasoning')

describe('useMultiStepReasoningActions', () => {
  it('calls API and shows success toast', async () => {
    const { result } = renderHook(() => useMultiStepReasoningActions())

    await act(async () => {
      await result.current.updateMultiStepReasoning('session-123', {
        multi_step_reasoning_enabled: true
      })
    })

    expect(mockEditMultiStepReasoning).toHaveBeenCalledWith('session-123', {
      multi_step_reasoning_enabled: true
    })
  })
})
```

## Related Patterns

- [Handlers](./useHandlers.md) - Consume actions in event handlers
- [Lifecycle](./useLifecycle.md) - May trigger actions on mount/unmount
