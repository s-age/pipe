## Special Purpose: `useInitialLoading`

`useInitialLoading` is a small utility for initial data fetching that executes only once, even in React StrictMode. It's useful for one-time setup calls on mount where duplicate invocations in development are undesirable.

```typescript
// Implementation
import { useEffect, useRef } from 'react'

export const useInitialLoading = (loadFunction: () => Promise<void>): void => {
  const initializedReference = useRef(false)

  useEffect(() => {
    if (initializedReference.current) {
      return
    }
    initializedReference.current = true
    void loadFunction()
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])
}
```

**When to use:** initial page data fetching on mount, one-time setup operations with side effects, API calls that should only happen once per component lifecycle.

**When NOT to use:** effects that should re-run on dependency changes or user-triggered actions.

# Lifecycle Pattern

## Purpose

Lifecycle hooks manage side effects using `useEffect`. They handle DOM interactions, event listeners, timers, focus management, and other operations that need to synchronize with the component lifecycle.

## Characteristics

- **Uses useEffect** - All side effects in useEffect hooks
- **Cleanup** - Properly removes event listeners, timers, subscriptions
- **No return value** - Typically returns void or refs
- **Passive** - Reacts to prop/state changes, doesn't handle user events directly
- **Internal helpers** - May contain helper functions not exported

## Naming Convention

```
use{ComponentName}Lifecycle
```

## Code Template

```typescript
import { useEffect, useRef } from 'react'

type Use{ComponentName}LifecycleProperties = {
  // Dependencies that affect side effects
  isActive: boolean
  onComplete?: () => void
}

export const use{ComponentName}Lifecycle = ({
  isActive,
  onComplete
}: Use{ComponentName}LifecycleProperties): void => {
  // Optional: refs for tracking state between renders
  const previousState = useRef(isActive)

  useEffect(() => {
    // Internal helper (not exported)
    const handleEvent = () => {
      // ... handle event
    }

    if (isActive) {
      // Set up side effect
      document.addEventListener('event', handleEvent)
    }

    // Cleanup function
    return () => {
      document.removeEventListener('event', handleEvent)
    }
  }, [isActive])

  useEffect(() => {
    // Another independent effect
    if (previousState.current && !isActive) {
      onComplete?.()
    }
    previousState.current = isActive
  }, [isActive, onComplete])
}
```

## Real Examples

### Click Outside Detection

```typescript
import { useEffect, useRef } from 'react'

type UseSelectLifecycleProperties = {
  isOpen: boolean
  close: () => void
  clearHighlight: () => void
}

export const useSelectLifecycle = ({
  isOpen,
  close,
  clearHighlight
}: UseSelectLifecycleProperties): {
  rootReference: React.RefObject<HTMLDivElement | null>
} => {
  const rootReference = useRef<HTMLDivElement | null>(null)

  useEffect(() => {
    if (!isOpen) return

    // Internal helper - not exported
    const handlePointerDown = (event: Event): void => {
      if (
        rootReference.current &&
        !rootReference.current.contains(event.target as Node)
      ) {
        close()
        clearHighlight()
      }
    }

    document.addEventListener('pointerdown', handlePointerDown)

    return () => {
      document.removeEventListener('pointerdown', handlePointerDown)
    }
  }, [isOpen, close, clearHighlight])

  return { rootReference }
}
```

### Focus Management

```typescript
import { useEffect, useRef } from 'react'

type UseInstructionFormLifecycleProperties = {
  isStreaming: boolean
}

export const useInstructionFormLifecycle = ({
  isStreaming
}: UseInstructionFormLifecycleProperties): void => {
  const previousStreamingState = useRef<boolean>(isStreaming)

  // Focus on initial mount
  useEffect(() => {
    setTimeout(() => {
      const textarea = document.getElementById(
        'new-instruction-text'
      ) as HTMLTextAreaElement | null
      if (textarea) {
        textarea.focus()
      }
    }, 0)
  }, [])

  // Focus when streaming completes
  useEffect(() => {
    if (previousStreamingState.current && !isStreaming) {
      // Streaming just finished
      setTimeout(() => {
        const textarea = document.getElementById(
          'new-instruction-text'
        ) as HTMLTextAreaElement | null
        if (textarea) {
          textarea.focus()
        }
      }, 0)
    }
    previousStreamingState.current = isStreaming
  }, [isStreaming])
}
```

### Auto-scroll

```typescript
import { useEffect, useRef } from 'react'

type UseSessionTreeLifecycleProperties = {
  sessions: Session[]
  currentSessionId: string | null
}

export const useSessionTreeLifecycle = ({
  sessions,
  currentSessionId
}: UseSessionTreeLifecycleProperties): void => {
  const scrolled = useRef(false)

  useEffect(() => {
    if (scrolled.current || !currentSessionId || sessions.length === 0) return

    setTimeout(() => {
      const element = document.getElementById(`session-${currentSessionId}`)
      if (element) {
        element.scrollIntoView({ behavior: 'smooth', block: 'center' })
        scrolled.current = true
      }
    }, 100)
  }, [sessions, currentSessionId])
}
```

### Timer Management

```tsx
import { useEffect } from 'react'

type UseToastItemLifecycleProperties = {
  id: string
  duration?: number
  onDismiss: (id: string) => void
}

export const useToastItemLifecycle = ({
  id,
  duration = 5000,
  onDismiss
}: UseToastItemLifecycleProperties): void => {
  useEffect(() => {
    if (duration === Infinity) return

    const timer = setTimeout(() => {
      onDismiss(id)
    }, duration)

    return () => {
      clearTimeout(timer)
    }
  }, [id, duration, onDismiss])
}
```

## Usage in Components

```typescript
import { useSelectLifecycle } from './hooks/useSelectLifecycle'

const Select = ({ isOpen, onClose }) => {
  const { rootReference } = useSelectLifecycle({
    isOpen,
    close: onClose,
    clearHighlight: () => {}
  })

  return (
    <div ref={rootReference}>
      {/* Select content */}
    </div>
  )
}
```

## Common Lifecycle Patterns

### 1. Event Listener Setup/Cleanup

```typescript
useEffect(() => {
  const handleEvent = () => {
    /* ... */
  }

  window.addEventListener('event', handleEvent)
  return () => window.removeEventListener('event', handleEvent)
}, [dependencies])
```

### 2. Timer/Interval

```typescript
useEffect(() => {
  const timer = setTimeout(() => {
    onTimeout()
  }, delay)

  return () => clearTimeout(timer)
}, [delay, onTimeout])
```

### 3. Focus/DOM Manipulation

```typescript
useEffect(() => {
  const element = elementRef.current
  if (element && shouldFocus) {
    element.focus()
  }
}, [shouldFocus])
```

### 4. Scroll Management

```typescript
useEffect(() => {
  if (shouldScroll) {
    element?.scrollIntoView({ behavior: 'smooth' })
  }
}, [shouldScroll, element])
```

### 5. State Tracking Between Renders

```typescript
useEffect(() => {
  if (previousValue.current !== currentValue) {
    // Value changed
    onChange(currentValue)
  }
  previousValue.current = currentValue
}, [currentValue, onChange])
```

## When to Use Lifecycle

✅ **Use Lifecycle when:**

- Setting up/tearing down event listeners
- Managing timers or intervals
- Focus management after render
- Scroll to element on mount/update
- Tracking state changes between renders
- Subscribing to external data sources
- DOM measurements or mutations

❌ **Don't use Lifecycle for:**

- User event handling (use Handlers)
- API calls triggered by user actions (use Actions + Handlers)
- Synchronous state derivation (use useMemo)

## Internal Helpers

Lifecycle hooks commonly contain internal helper functions that are not exported:

```typescript
export const useSelectLifecycle = ({ isOpen, close }) => {
  useEffect(() => {
    // ✅ This is fine - handlePointerDown is an internal helper
    const handlePointerDown = (event: Event) => {
      if (shouldClose(event)) {
        close()
      }
    }

    document.addEventListener('pointerdown', handlePointerDown)
    return () => document.removeEventListener('pointerdown', handlePointerDown)
  }, [isOpen, close])
}
```

**Why this is acceptable:**

- The helper is scoped to the effect
- It's not reusable outside this hook
- It keeps the code clean and readable
- It follows the closure pattern for event handlers

## Multiple Effects

It's perfectly fine to have multiple `useEffect` calls in one lifecycle hook:

```typescript
export const useInstructionFormLifecycle = ({ isStreaming }) => {
  // Effect 1: Focus on mount
  useEffect(() => {
    focusTextarea()
  }, [])

  // Effect 2: Focus when streaming completes
  useEffect(() => {
    if (previousState.current && !isStreaming) {
      focusTextarea()
    }
    previousState.current = isStreaming
  }, [isStreaming])
}
```

**When to split effects:**

- Different dependencies
- Different cleanup logic
- Conceptually separate concerns

**When to combine effects:**

- Tightly coupled operations
- Share same dependencies
- Need to run in specific order

## Testing Lifecycle

```typescript
import { renderHook } from '@testing-library/react'
import { useSelectLifecycle } from './useSelectLifecycle'

describe('useSelectLifecycle', () => {
  it('calls close when clicking outside', () => {
    const mockClose = jest.fn()
    const mockClearHighlight = jest.fn()

    const { result } = renderHook(() =>
      useSelectLifecycle({
        isOpen: true,
        close: mockClose,
        clearHighlight: mockClearHighlight
      })
    )

    // Simulate click outside
    const outsideElement = document.createElement('div')
    document.body.appendChild(outsideElement)

    act(() => {
      outsideElement.click()
    })

    expect(mockClose).toHaveBeenCalled()
    expect(mockClearHighlight).toHaveBeenCalled()
  })
})
```

## Best Practices

1. **Always cleanup** - Remove listeners, cancel timers, unsubscribe
2. **Guard conditions** - Early return if effect shouldn't run
3. **Use refs for non-reactive values** - Previous state, timers, element refs
4. **Separate effects** - One effect per concern when possible
5. **Internal helpers OK** - Keep helper functions inside the effect
6. **Return void** - Unless returning refs needed by component
7. **Type dependencies** - Ensure proper TypeScript types for all deps

## Related Patterns

- [Actions](./useActions.md) - May be called from lifecycle on mount
- [Handlers](./useHandlers.md) - May trigger effects indirectly through state changes
