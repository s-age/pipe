# Atoms Layer

## Purpose

Atoms are the smallest, most fundamental UI building blocks. They are pure, presentational components that render basic HTML elements with consistent styling and behavior.

## Responsibilities

1. **Basic UI Elements** - Render buttons, inputs, icons, labels, headings
2. **Consistent Styling** - Provide design system variants and themes
3. **Accessibility** - Implement proper HTML semantics and ARIA attributes
4. **Type Safety** - Extend native HTML element types
5. **Pure Presentation** - No logic, no state, only rendering

## Characteristics

- ✅ Render single HTML elements (sometimes with wrapper)
- ✅ Accept native HTML attributes via Props
- ✅ Provide style variants (size, color, kind)
- ✅ Use TypeScript for strict typing
- ✅ Forward refs when needed
- ❌ **NO state** (not even local UI state)
- ❌ **NO Store access**
- ❌ **NO business logic**
- ❌ **NO API calls**
- ❌ **NO custom hooks** (except for refs/forwarding)

## File Structure

```
atoms/
└── Button/
    ├── index.tsx        # Component
    └── style.css.ts     # Vanilla Extract styles
```

No `hooks/` directory - atoms should be pure and stateless.

## Template

```typescript
import clsx from 'clsx'
import type { {Element}HTMLAttributes, JSX } from 'react'
import { baseStyle } from './style.css'

type {Name}Properties = {
  variant?: 'primary' | 'secondary'
  size?: 'small' | 'medium' | 'large'
} & {Element}HTMLAttributes<HTML{Element}Element>

export const {Name} = ({
  variant = 'primary',
  size = 'medium',
  className,
  ...properties
}: {Name}Properties): JSX.Element => (
  <{element}
    className={clsx(baseStyle({ variant, size }), className)}
    {...properties}
  />
)
```

## Real Examples

### Button

```typescript
import clsx from 'clsx'
import type { ButtonHTMLAttributes, JSX } from 'react'
import { button } from './style.css'

type ButtonProperties = {
  kind?: 'primary' | 'secondary' | 'ghost'
  size?: 'small' | 'default' | 'large' | 'xsmall'
  text?: 'bold' | 'uppercase'
  hasBorder?: boolean
} & ButtonHTMLAttributes<HTMLButtonElement>

export const Button = ({
  kind = 'primary',
  size = 'default',
  text,
  hasBorder = true,
  className,
  ...properties
}: ButtonProperties): JSX.Element => (
  <button
    className={clsx(button({ kind, size, text, hasBorder }), className)}
    {...properties}
  />
)
```

### InputText

```typescript
import clsx from 'clsx'
import { forwardRef } from 'react'
import type { InputHTMLAttributes, JSX } from 'react'
import { input } from './style.css'

type InputTextProperties = {
  hasError?: boolean
} & InputHTMLAttributes<HTMLInputElement>

export const InputText = forwardRef<HTMLInputElement, InputTextProperties>(
  ({ hasError, className, ...properties }, ref): JSX.Element => (
    <input
      ref={ref}
      type="text"
      className={clsx(input({ hasError }), className)}
      {...properties}
    />
  )
)

InputText.displayName = 'InputText'
```

### Label

```typescript
import clsx from 'clsx'
import type { LabelHTMLAttributes, JSX } from 'react'
import { label } from './style.css'

type LabelProperties = {
  required?: boolean
} & LabelHTMLAttributes<HTMLLabelElement>

export const Label = ({
  required,
  children,
  className,
  ...properties
}: LabelProperties): JSX.Element => (
  <label className={clsx(label, className)} {...properties}>
    {children}
    {required && <span aria-label="required"> *</span>}
  </label>
)
```

### Icon

```typescript
import type { SVGAttributes, JSX } from 'react'
import { icon } from './style.css'

type IconDeleteProperties = {
  size?: number
} & SVGAttributes<SVGSVGElement>

export const IconDelete = ({
  size = 20,
  ...properties
}: IconDeleteProperties): JSX.Element => (
  <svg
    width={size}
    height={size}
    viewBox="0 0 20 20"
    className={icon}
    {...properties}
  >
    <path d="M8 15A.5.5 0 0 0 8.5 15.5H11.5A.5.5 0 0 0 12 15V9A.5.5 0 0 0 11.5 8.5H8.5A.5.5 0 0 0 8 9V15Z" />
    {/* ... more path elements */}
  </svg>
)
```

### Heading

```typescript
import clsx from 'clsx'
import type { HTMLAttributes, JSX } from 'react'
import { heading } from './style.css'

type HeadingProperties = {
  level?: 1 | 2 | 3 | 4 | 5 | 6
  size?: 'small' | 'medium' | 'large'
} & HTMLAttributes<HTMLHeadingElement>

export const Heading = ({
  level = 2,
  size = 'medium',
  className,
  children,
  ...properties
}: HeadingProperties): JSX.Element => {
  const Tag = `h${level}` as const

  return (
    <Tag
      className={clsx(heading({ size }), className)}
      {...properties}
    >
      {children}
    </Tag>
  )
}
```

## Best Practices

### 1. Extend Native HTML Attributes

Always extend the appropriate HTML element type:

```typescript
// ✅ Good - Extends native attributes
type ButtonProperties = {
  kind?: 'primary' | 'secondary'
} & ButtonHTMLAttributes<HTMLButtonElement>

// ❌ Bad - Custom props only
type ButtonProperties = {
  kind?: 'primary' | 'secondary'
  onClick?: () => void
  disabled?: boolean
}
```

### 2. Use forwardRef for Form Elements

Form elements need ref forwarding:

```typescript
import { forwardRef } from 'react'

export const InputText = forwardRef<HTMLInputElement, InputTextProperties>(
  (props, ref) => <input ref={ref} {...props} />
)

InputText.displayName = 'InputText'
```

### 3. Provide Style Variants

Use Vanilla Extract for type-safe variants:

```typescript
// style.css.ts
import { recipe } from '@vanilla-extract/recipes'

export const button = recipe({
  base: {
    padding: '8px 16px',
    borderRadius: '4px',
    cursor: 'pointer'
  },
  variants: {
    kind: {
      primary: { background: 'blue', color: 'white' },
      secondary: { background: 'gray', color: 'black' }
    },
    size: {
      small: { fontSize: '12px' },
      medium: { fontSize: '14px' },
      large: { fontSize: '16px' }
    }
  },
  defaultVariants: {
    kind: 'primary',
    size: 'medium'
  }
})
```

### 4. Accept className for Extensibility

Allow consumers to add custom styles:

```typescript
export const Button = ({ className, ...props }) => (
  <button
    className={clsx(baseStyle, className)}  // Merge styles
    {...props}
  />
)
```

### 5. Implement Accessibility

```typescript
// ARIA attributes
<button
  aria-label="Close dialog"
  aria-pressed={isPressed}
  role="button"
>
  ×
</button>

// Semantic HTML
<label htmlFor="email">Email</label>
<input id="email" type="email" />

// Required indicator
<label>
  Username {required && <span aria-label="required">*</span>}
</label>
```

### 6. Keep Pure and Stateless

```typescript
// ✅ Good - Pure, stateless
export const Button = ({ onClick, children }) => (
  <button onClick={onClick}>{children}</button>
)

// ❌ Bad - Has state
export const Button = ({ children }) => {
  const [clicked, setClicked] = useState(false)
  return <button onClick={() => setClicked(true)}>{children}</button>
}
```

## Common Atom Patterns

### Button Variants

```typescript
<Button kind="primary">Primary</Button>
<Button kind="secondary">Secondary</Button>
<Button kind="ghost">Ghost</Button>
<Button size="small">Small</Button>
<Button disabled>Disabled</Button>
```

### Form Inputs

```typescript
<InputText placeholder="Enter text" />
<InputText type="email" />
<InputText hasError />
<InputCheckbox checked />
<InputRadio name="option" value="1" />
```

### Typography

```typescript
<Heading level={1}>Page Title</Heading>
<Heading level={2} size="large">Section</Heading>
<Label>Field Label</Label>
<ErrorMessage>Error text</ErrorMessage>
```

### Icons

```typescript
<IconDelete size={16} />
<IconEdit onClick={handleEdit} />
<IconCopy aria-label="Copy to clipboard" />
```

### Loading

```typescript
<LoadingSpinner size="small" />
<LoadingSpinner color="blue" />
```

## Testing Atoms

### Snapshot Tests

```typescript
import { render } from '@testing-library/react'
import { Button } from './index'

describe('Button', () => {
  it('renders primary button', () => {
    const { container } = render(<Button kind="primary">Click me</Button>)
    expect(container).toMatchSnapshot()
  })

  it('renders all variants', () => {
    const { container } = render(
      <>
        <Button kind="primary">Primary</Button>
        <Button kind="secondary">Secondary</Button>
        <Button size="small">Small</Button>
      </>
    )
    expect(container).toMatchSnapshot()
  })
})
```

### Behavior Tests

```typescript
import { render, screen, fireEvent } from '@testing-library/react'
import { Button } from './index'

describe('Button', () => {
  it('calls onClick when clicked', () => {
    const handleClick = jest.fn()
    render(<Button onClick={handleClick}>Click</Button>)

    fireEvent.click(screen.getByText('Click'))
    expect(handleClick).toHaveBeenCalledTimes(1)
  })

  it('does not call onClick when disabled', () => {
    const handleClick = jest.fn()
    render(<Button onClick={handleClick} disabled>Click</Button>)

    fireEvent.click(screen.getByText('Click'))
    expect(handleClick).not.toHaveBeenCalled()
  })
})
```

### Accessibility Tests

```typescript
import { render } from '@testing-library/react'
import { axe, toHaveNoViolations } from 'jest-axe'

expect.extend(toHaveNoViolations)

describe('Button accessibility', () => {
  it('should not have accessibility violations', async () => {
    const { container } = render(<Button>Accessible Button</Button>)
    const results = await axe(container)
    expect(results).toHaveNoViolations()
  })
})
```

## When to Create an Atom

Create an atom when:

- ✅ Single HTML element (button, input, label)
- ✅ Need consistent styling across app
- ✅ Pure presentational component
- ✅ No internal state or logic

Promote to molecule when:

- ❌ Combining multiple atoms
- ❌ Need local UI state
- ❌ Has internal logic

## Atoms vs Molecules Decision Tree

```
Is it a single HTML element?
├─ Yes → Atom (Button, Input, Label)
└─ No → Is it combining 2+ atoms?
    ├─ Yes → Does it need UI state?
    │   ├─ Yes → Molecule (Select, Modal, Tooltip)
    │   └─ No → Might be Atom or Molecule
    └─ No → Atom (Icon, LoadingSpinner)
```

## Style Guidelines

### Use Vanilla Extract

```typescript
// style.css.ts
import { style } from '@vanilla-extract/css'
import { recipe } from '@vanilla-extract/recipes'

export const button = recipe({
  base: {
    fontFamily: 'system-ui',
    fontWeight: 500,
    transition: 'all 0.2s'
  },
  variants: {
    kind: {
      primary: {
        backgroundColor: '#0070f3',
        color: 'white'
      }
    }
  }
})
```

### Design Tokens

```typescript
// tokens.css.ts
export const colors = {
  primary: '#0070f3',
  secondary: '#666',
  danger: '#ff0000'
}

export const spacing = {
  small: '8px',
  medium: '16px',
  large: '24px'
}
```

## Common Anti-patterns

❌ **State in Atoms**

```typescript
// ❌ Bad
export const Button = () => {
  const [clicked, setClicked] = useState(false)
  // Atoms should not have state
}
```

❌ **Business Logic**

```typescript
// ❌ Bad
export const Button = ({ sessionId }) => {
  const handleClick = async () => {
    await updateSession(sessionId) // No API calls in atoms
  }
}
```

❌ **Store Access**

```typescript
// ❌ Bad
export const Button = () => {
  const { pushToast } = useAppStore() // No store access
}
```

❌ **Complex Composition**

```typescript
// ❌ Bad - Should be a Molecule
export const Button = () => (
  <button>
    <Icon />
    <Label />
    <Badge />
  </button>
)
```

## Related Documentation

- [Components Overview](./components.md) - Architecture overview
- [Molecules](./molecules.md) - How molecules compose atoms
- [Design System](../../design-system.md) - Style guidelines (if exists)
