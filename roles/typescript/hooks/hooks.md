# Custom Hooks Guidelines

## Philosophy

This project does **not impose strict limitations** on custom hook types or patterns. You are free to create hooks that best serve your component's needs. However, we encourage organizing hooks by their primary responsibility to improve maintainability and discoverability.

## Recommended Patterns

While there are no restrictions, we've identified **three common patterns** that handle most use cases:

1. **[Actions](./useActions.md)** - Pure API call wrappers
2. **[Handlers](./useHandlers.md)** - UI event processing logic
3. **[Lifecycle](./useLifecycle.md)** - Side effects and lifecycle management

These patterns provide clear separation of concerns and make code easier to reason about.

## Naming Convention

When following the recommended patterns, use this naming convention:

```
use{ComponentName}{Actions|Handlers|Lifecycle}
```

**Examples:**

- `useSessionMetaActions` - API calls for SessionMeta
- `useInstructionFormHandlers` - Event handlers for InstructionForm
- `useSelectLifecycle` - Side effects for Select component

## Exceptions to Patterns

Some hooks naturally fall outside these patterns and should follow domain-specific naming:

### Context Hooks

Hooks that provide or consume React Context:

```typescript
// Context definition and consumer hooks
export const FormContext = createContext<FormMethods | undefined>(undefined)

export const useFormContext = (): FormMethods => {
  const context = useContext(FormContext)
  if (!context) throw new Error('useFormContext must be used within a Form')
  return context
}

export const useOptionalFormContext = (): FormMethods | undefined => {
  return useContext(FormContext)
}
```

**Files:** `*Context.tsx`, `*Provider.tsx`

### Integration Hooks

Hooks that integrate with form libraries or provide complex state management:

```typescript
// Form field integration
export const useInputText = ({ name, register, ...props }) => {
  const form = useOptionalFormContext()
  const registerProperties = register?.(name) ?? form?.register(name)
  // Returns registerProperties, handlers, and component-specific logic
}

// Complex state + handlers combination
export const useSelect = ({ name, options, register }) => {
  // State management
  const [isOpen, setIsOpen] = useState(false)
  const [selectedValue, setSelectedValue] = useState(defaultValue)

  // Form integration
  const registerProperties = register?.(name)

  // Option processing
  const filteredOptions = useMemo(...)

  // Returns state, setters, and computed values
}
```

**Examples:**

- `useInputText` - Input field with form integration
- `useTextArea` - Textarea with form integration
- `useSelect` - Select dropdown with state + form integration
- `useModal` - Modal state consumer
- `useToast` - Toast notification API

### Utility Hooks

General-purpose hooks that don't fit the Actions/Handlers/Lifecycle pattern:

```typescript
// DOM utilities
export const useClickOutside = (ref, handler) => { ... }
export const useDebounce = (value, delay) => { ... }

// State utilities
export const useLocalStorage = (key, defaultValue) => { ... }
export const usePrevious = (value) => { ... }
```

## Guidelines for Creating New Hooks

1. **Start with clarity** - Choose a name that clearly describes what the hook does
2. **Consider the patterns** - If your hook fits Actions/Handlers/Lifecycle, follow that convention
3. **Don't force patterns** - If a hook doesn't fit, use a descriptive name instead
4. **Colocate related hooks** - Keep hooks in a `hooks/` directory near their component
5. **Document exceptions** - If creating a new pattern, document it here

## Hook Composition

Hooks often work together. Here's a typical composition:

```typescript
// In component
const MyComponent = () => {
  // 1. Actions (API calls)
  const { updateSession } = useMyComponentActions()

  // 2. Handlers (uses actions)
  const { handleSubmit } = useMyComponentHandlers({ updateSession })

  // 3. Lifecycle (side effects)
  useMyComponentLifecycle({ isLoading })

  return <form onSubmit={handleSubmit}>...</form>
}
```

## Internal Helpers

Hooks may contain internal helper functions that are not exported. This is perfectly acceptable:

```typescript
export const useSelectLifecycle = ({ isOpen, close }) => {
  const rootRef = useRef(null)

  useEffect(() => {
    // Internal helper - not exported
    const handlePointerDown = (event) => {
      if (rootRef.current && !rootRef.current.contains(event.target)) {
        close()
      }
    }

    document.addEventListener('pointerdown', handlePointerDown)
    return () => document.removeEventListener('pointerdown', handlePointerDown)
  }, [isOpen, close])

  return { rootRef }
}
```

## Further Reading

- [Actions Pattern](./useActions.md) - API call wrappers
- [Handlers Pattern](./useHandlers.md) - UI event processing
- [Lifecycle Pattern](./useLifecycle.md) - Side effects management
