# Molecules Layer

## Purpose

Molecules are composite UI components that combine multiple Atoms to create reusable interface elements. They handle local UI state but contain no business logic or API calls.

## Responsibilities

1. **Composite UI** - Combine 2-3+ atoms into functional units
2. **Local UI State** - Manage component-specific state (open/closed, hover, focus)
3. **User Input** - Handle form inputs and validation display
4. **Reusability** - Provide consistent UI patterns across the application
5. **Accessibility** - Implement proper ARIA attributes and keyboard navigation

## Characteristics

- ✅ Combine multiple Atoms
- ✅ Manage local UI state (isOpen, isFocused, etc.)
- ✅ Use custom hooks for UI logic
- ✅ Accept Props for data and callbacks
- ✅ Integrate with form libraries (react-hook-form)
- ❌ **NO Store access** (neither useAppStore nor page stores)
- ❌ **NO API calls** (delegate to Organisms/Pages)
- ❌ **NO business logic** (only UI logic)

## File Structure

```
molecules/
└── Select/
    ├── index.tsx                  # Main molecule component
    ├── style.css.ts               # Component styles
    └── hooks/
        ├── useSelect.ts           # State management + form integration
        ├── useSelectHandlers.ts   # Event handlers
        └── useSelectLifecycle.ts  # UI side effects (click outside)
```

## Template

```typescript
import type { JSX } from 'react'
import { SomeAtom } from '@/components/atoms/SomeAtom'
import { AnotherAtom } from '@/components/atoms/AnotherAtom'
import { useMolecule{Name} } from './hooks/useMolecule{Name}'

type {Name}Properties = {
  value?: string
  onChange?: (value: string) => void
  placeholder?: string
  disabled?: boolean
}

export const {Name} = ({
  value,
  onChange,
  placeholder,
  disabled
}: {Name}Properties): JSX.Element => {
  // Local UI state and handlers
  const {
    localValue,
    isOpen,
    handleClick,
    handleChange
  } = useMolecule{Name}({ value, onChange })

  return (
    <div>
      <SomeAtom
        value={localValue}
        onClick={handleClick}
        disabled={disabled}
      />
      {isOpen && (
        <AnotherAtom
          onChange={handleChange}
          placeholder={placeholder}
        />
      )}
    </div>
  )
}
```

## Real Example: Select

```typescript
import type { SelectHTMLAttributes, JSX } from 'react'
import type { UseFormRegister } from 'react-hook-form'
import { useSelect, type SelectOption } from './hooks/useSelect'
import { useSelectHandlers } from './hooks/useSelectHandlers'
import { useSelectUI } from './hooks/useSelectLifecycle'
import { selectStyle, trigger, panel, option } from './style.css'

type SelectProperties = {
  register?: UseFormRegister<Record<string, unknown>>
  name?: string
  options?: Array<string | SelectOption>
  searchable?: boolean
  placeholder?: string
} & SelectHTMLAttributes<HTMLSelectElement>

export const Select = (properties: SelectProperties): JSX.Element => {
  const {
    register,
    name,
    options,
    searchable = false,
    placeholder,
    className,
    ...rest
  } = properties

  // State management + form integration
  const {
    registerProperties,
    normalizedOptions,
    filteredOptions,
    selectedValue,
    isOpen,
    setIsOpen,
    query,
    setQuery,
    listReference,
    highlightedIndex,
    setHighlightedIndex,
    setSelectedValue
  } = useSelect({
    register,
    name,
    options,
    defaultValue: rest.defaultValue as string | undefined,
    searchable
  })

  // Event handlers
  const {
    toggleOpen,
    close,
    clearHighlight,
    handleSelect,
    handleSearchChange,
    handleKeyDown,
    handleMouseEnter,
    handleMouseLeave
  } = useSelectHandlers({
    isOpen,
    setIsOpen,
    filteredOptions,
    highlightedIndex,
    setHighlightedIndex,
    setSelectedValue,
    setQuery,
    listReference
  })

  // UI lifecycle (click outside detection)
  const { rootReference } = useSelectUI({
    isOpen,
    close,
    clearHighlight
  })

  const selectedOption = normalizedOptions.find(
    (opt) => opt.value === selectedValue
  )

  return (
    <div ref={rootReference} className={selectStyle}>
      {/* Hidden input for form integration */}
      <input type="hidden" {...registerProperties} value={selectedValue || ''} />

      {/* Trigger button */}
      <button
        type="button"
        className={trigger}
        onClick={toggleOpen}
        aria-haspopup="listbox"
        aria-expanded={isOpen}
      >
        {selectedOption?.label || placeholder || 'Select...'}
      </button>

      {/* Dropdown panel */}
      {isOpen && (
        <div className={panel} role="listbox">
          {searchable && (
            <input
              type="text"
              value={query}
              onChange={handleSearchChange}
              placeholder="Search..."
              autoFocus
            />
          )}

          <ul ref={listReference}>
            {filteredOptions.map((opt, index) => (
              <li
                key={opt.value}
                role="option"
                aria-selected={opt.value === selectedValue}
                className={index === highlightedIndex ? optionHighlighted : option}
                onClick={() => handleSelect(opt.value)}
                onMouseEnter={() => handleMouseEnter(index)}
                onMouseLeave={handleMouseLeave}
                onKeyDown={handleKeyDown}
              >
                {opt.label}
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  )
}
```

## Custom Hooks Pattern for Molecules

## New Molecule: Accordion

Use `Accordion` for compact/expandable panels. The molecule is accessibility-minded (keyboard toggling, `aria-expanded` / `aria-controls`) and accepts a `title`, optional `summary` shown when collapsed, and children shown when expanded.

API (summary):

```tsx
type AccordionProps = {
  title: React.ReactNode
  summary?: React.ReactNode
  defaultOpen?: boolean
  children?: React.ReactNode
}

;<Accordion
  title={<Header />}
  summary={<small>TTL: 3 · 有効</small>}
  defaultOpen={false}
>
  {/* details shown when expanded */}
</Accordion>
```

Pattern: use `Accordion` at the molecules layer for UI-only expand/collapse behavior. Keep `defaultOpen` false for lists where density matters and surface detail editing inside the panel.

### State Management Hook

Manages component state and form integration:

```typescript
// hooks/useSelect.ts
import { useMemo, useState } from 'react'
import { useOptionalFormContext } from '@/components/organisms/Form'

export const useSelect = ({ name, options, register, defaultValue }) => {
  // Form integration
  const form = useOptionalFormContext()
  const registerProperties = register?.(name) ?? form?.register(name)

  // Local UI state
  const [isOpen, setIsOpen] = useState(false)
  const [query, setQuery] = useState('')
  const [selectedValue, setSelectedValue] = useState(defaultValue)
  const [highlightedIndex, setHighlightedIndex] = useState(-1)

  // Computed values
  const normalizedOptions = useMemo(
    () =>
      options.map((opt) =>
        typeof opt === 'string' ? { value: opt, label: opt } : opt
      ),
    [options]
  )

  const filteredOptions = useMemo(
    () =>
      normalizedOptions.filter((opt) =>
        opt.label.toLowerCase().includes(query.toLowerCase())
      ),
    [normalizedOptions, query]
  )

  return {
    registerProperties,
    normalizedOptions,
    filteredOptions,
    selectedValue,
    setSelectedValue,
    isOpen,
    setIsOpen,
    query,
    setQuery,
    highlightedIndex,
    setHighlightedIndex
  }
}
```

### Event Handlers Hook

Handles user interactions:

```typescript
// hooks/useSelectHandlers.ts
import { useCallback } from 'react'

export const useSelectHandlers = ({
  isOpen,
  setIsOpen,
  setSelectedValue,
  setQuery,
  setHighlightedIndex
}) => {
  const toggleOpen = useCallback(() => {
    setIsOpen(!isOpen)
  }, [isOpen, setIsOpen])

  const close = useCallback(() => {
    setIsOpen(false)
  }, [setIsOpen])

  const handleSelect = useCallback(
    (value: string) => {
      setSelectedValue(value)
      setIsOpen(false)
      setQuery('')
    },
    [setSelectedValue, setIsOpen, setQuery]
  )

  const handleKeyDown = useCallback(
    (event: React.KeyboardEvent) => {
      if (event.key === 'Enter') {
        // Handle selection
      } else if (event.key === 'ArrowDown') {
        setHighlightedIndex((prev) => prev + 1)
      } else if (event.key === 'ArrowUp') {
        setHighlightedIndex((prev) => Math.max(0, prev - 1))
      }
    },
    [setHighlightedIndex]
  )

  return {
    toggleOpen,
    close,
    handleSelect,
    handleKeyDown
  }
}
```

### Lifecycle Hook

Handles side effects:

```typescript
// hooks/useSelectLifecycle.ts
import { useEffect, useRef } from 'react'

export const useSelectUI = ({ isOpen, close, clearHighlight }) => {
  const rootReference = useRef<HTMLDivElement | null>(null)

  useEffect(() => {
    if (!isOpen) return

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
    return () => document.removeEventListener('pointerdown', handlePointerDown)
  }, [isOpen, close, clearHighlight])

  return { rootReference }
}
```

## Best Practices

### 1. Accept Props for All External Data

Never access stores - only use Props:

```typescript
// ✅ Good - Props only
type Props = {
  value: string
  options: string[]
  onChange: (value: string) => void
}

// ❌ Bad - Store access
const BadMolecule = () => {
  const { data } = useAppStore() // NOT ALLOWED!
}
```

### 2. Manage Only Local UI State

```typescript
// ✅ Good - Local UI state
const [isOpen, setIsOpen] = useState(false)
const [isFocused, setIsFocused] = useState(false)

// ❌ Bad - Domain state
const [sessionData, setSessionData] = useState() // Use Props instead
```

### 3. Integrate with Form Libraries

```typescript
import { useOptionalFormContext } from '@/components/organisms/Form'

export const InputField = ({ name, register, ...props }) => {
  const form = useOptionalFormContext()
  const registerProperties = register?.(name) ?? form?.register(name)

  return <input {...registerProperties} {...props} />
}
```

### 4. Handle Accessibility

```typescript
<button
  aria-haspopup="listbox"
  aria-expanded={isOpen}
  aria-label="Select option"
  role="combobox"
>
  {label}
</button>
```

### 5. Provide Flexible Styling

```typescript
type Props = {
  className?: string
}

export const Molecule = ({ className, ...props }: Props) => (
  <div className={clsx(defaultStyle, className)}>
    {/* ... */}
  </div>
)
```

## Common Molecule Patterns

### Input Group

```typescript
export const InputField = ({ name, label, error, ...props }) => (
  <div className={fieldContainer}>
    <Label htmlFor={name}>{label}</Label>
    <InputText id={name} name={name} {...props} />
    {error && <ErrorMessage>{error}</ErrorMessage>}
  </div>
)
```

### Card

```typescript
export const Card = ({ title, children, actions }) => (
  <div className={card}>
    <div className={cardHeader}>
      <Heading level={3}>{title}</Heading>
    </div>
    <div className={cardBody}>
      {children}
    </div>
    {actions && (
      <div className={cardFooter}>
        {actions}
      </div>
    )}
  </div>
)
```

### Modal

```typescript
export const Modal = ({ isOpen, onClose, title, children }) => {
  if (!isOpen) return null

  return (
    <div className={overlay} onClick={onClose}>
      <div className={modal} onClick={e => e.stopPropagation()}>
        <div className={modalHeader}>
          <Heading>{title}</Heading>
          <Button onClick={onClose}>×</Button>
        </div>
        <div className={modalBody}>
          {children}
        </div>
      </div>
    </div>
  )
}
```

### Tooltip

```typescript
export const Tooltip = ({ content, children }) => {
  const [isVisible, setIsVisible] = useState(false)

  return (
    <div
      onMouseEnter={() => setIsVisible(true)}
      onMouseLeave={() => setIsVisible(false)}
    >
      {children}
      {isVisible && (
        <div className={tooltip}>
          {content}
        </div>
      )}
    </div>
  )
}
```

## Testing Molecules

### Component Tests

```typescript
import { render, screen, fireEvent } from '@testing-library/react'
import { Select } from './index'

describe('Select', () => {
  it('opens dropdown on click', () => {
    const options = ['Option 1', 'Option 2']
    render(<Select options={options} />)

    const trigger = screen.getByRole('combobox')
    fireEvent.click(trigger)

    expect(screen.getByRole('listbox')).toBeInTheDocument()
    expect(screen.getByText('Option 1')).toBeInTheDocument()
  })

  it('calls onChange when option selected', () => {
    const handleChange = jest.fn()
    const options = ['Option 1', 'Option 2']

    render(<Select options={options} onChange={handleChange} />)

    fireEvent.click(screen.getByRole('combobox'))
    fireEvent.click(screen.getByText('Option 1'))

    expect(handleChange).toHaveBeenCalledWith('Option 1')
  })
})
```

## When to Create a Molecule

Create a molecule when:

- ✅ Combining 2-3+ atoms with UI logic
- ✅ Need consistent UI pattern across app
- ✅ Has local state (open/closed, focus)
- ✅ Form input with label + error display

Use an atom instead when:

- ❌ Single HTML element
- ❌ No internal state
- ❌ Pure styling wrapper

Promote to organism when:

- ❌ Needs API calls
- ❌ Has business logic
- ❌ Needs Store access

## Related Documentation

- [Components Overview](./components.md) - Architecture overview
- [Organisms](./organisms.md) - How organisms use molecules
- [Atoms](./atoms.md) - Building blocks of molecules
- [Custom Hooks](../hooks/hooks.md) - Hook patterns for UI logic
