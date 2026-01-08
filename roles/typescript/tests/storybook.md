# Role: Storybook Story Creation (TypeScript)

## Overview

This role defines **HOW** to create Storybook stories for React components using TypeScript. It covers patterns for atoms, molecules, and organisms following the project's atomic design structure.

## Core Principles

1. **Visual Documentation** - Stories demonstrate all visual states and interactions
2. **Type Safety** - Use TypeScript's `Meta` and `StoryObj` types from `@storybook/react-vite`
3. **Accessibility First** - Include ARIA attributes and accessibility examples
4. **Reusability** - Follow established patterns from existing stories
5. **Layer Awareness** - Different atomic layers require different story complexity

## Story File Structure

### Location Patterns

Stories are placed in one of two locations:

1. **Co-located with component** (preferred for new stories):
   ```
   ComponentName/
   ├── index.tsx
   ├── style.css.ts
   └── __stories__/
       └── ComponentName.stories.tsx
   ```

2. **Legacy pattern** (some existing components):
   ```
   ComponentName/
   ├── index.tsx
   ├── style.css.ts
   └── ComponentName.stories.tsx
   ```

**Recommendation**: Use the `__stories__/` subdirectory for all new stories.

### Basic Story Template

```typescript
import type { Meta as StoryMeta, StoryObj } from '@storybook/react-vite'
import type { JSX } from 'react'

import { ComponentName } from '../index'

const Meta = {
  title: 'Layer/ComponentName',
  component: ComponentName,
  tags: ['autodocs']
} satisfies StoryMeta<typeof ComponentName>

export default Meta

type Story = StoryObj<typeof Meta>

export const Default: Story = {
  args: {
    // Default props
  }
}
```

## Layer-Specific Patterns

### Atoms (Simple UI Elements)

**Characteristics**:
- No internal state or complex logic
- Focus on visual variants and props
- Minimal setup required

**Recommended Story Count**: 2-4 stories per atom

**Pattern**:
```typescript
import type { Meta as StoryMeta, StoryObj } from '@storybook/react-vite'

import { Button } from '../index'

const Meta = {
  title: 'Atoms/Button',
  component: Button,
  tags: ['autodocs']
} satisfies StoryMeta<typeof Button>

export default Meta
type Story = StoryObj<typeof Meta>

// 1. Default state
export const Default: Story = {
  args: {
    children: 'Click me'
  }
}

// 2. Variants (kind, size, etc.)
export const Primary: Story = {
  args: {
    kind: 'primary',
    children: 'Primary Button'
  }
}

export const Secondary: Story = {
  args: {
    kind: 'secondary',
    children: 'Secondary Button'
  }
}

// 3. States (disabled, loading, etc.)
export const Disabled: Story = {
  args: {
    disabled: true,
    children: 'Disabled Button'
  }
}

// 4. Sizes
export const Small: Story = {
  args: {
    size: 'small',
    children: 'Small'
  }
}

export const Large: Story = {
  args: {
    size: 'large',
    children: 'Large'
  }
}
```

**Atoms Example Variants**:
- **Text/Heading**: Different sizes, weights, colors
- **Icons**: Different states (default, hover, disabled)
- **LoadingSpinner**: Different sizes
- **ErrorMessage**: With/without icon

### Molecules (Form Elements & Layouts)

**Characteristics**:
- May have internal state
- Often integrate with React Hook Form
- Require 3 story patterns: Default, Controlled, RHF integration

**Recommended Story Count**: 3-5 stories per molecule

**Pattern 1: Simple Props**
```typescript
import type { Meta as StoryMeta, StoryObj } from '@storybook/react-vite'

import { InputText } from '../index'

const Meta = {
  title: 'Molecules/InputText',
  component: InputText,
  tags: ['autodocs']
} satisfies StoryMeta<typeof InputText>

export default Meta
type Story = StoryObj<typeof Meta>

export const Default: Story = {
  args: {
    placeholder: 'Type here…',
    name: 'simpleText',
    'aria-label': 'Simple text input'
  }
}
```

**Pattern 2: Controlled Component**
```typescript
import { useState } from 'react'
import type { JSX } from 'react'

export const Controlled: Story = {
  render: (): JSX.Element => {
    const ControlledExample = (): JSX.Element => {
      const [value, setValue] = useState('initial value')

      return (
        <div>
          <InputText
            value={value}
            onChange={(e) => setValue(e.target.value)}
            aria-label="Controlled input"
          />
          <div style={{ marginTop: 8 }}>Current: {value}</div>
        </div>
      )
    }

    return <ControlledExample />
  }
}
```

**Pattern 3: React Hook Form Integration**
```typescript
import { Form } from '@/components/organisms/Form'

export const WithRHF: Story = {
  render: (): JSX.Element => {
    const FormExample = (): JSX.Element => (
      <Form>
        <InputText
          name="fieldName"
          placeholder="Enter value"
          aria-label="Field label"
          aria-required={true}
        />
        <button type="submit" onClick={(data) => console.log('submit', data)}>
          Submit
        </button>
      </Form>
    )

    return <FormExample />
  }
}
```

**Molecules Example Variants**:
- **Form Inputs**: Default, Controlled, WithRHF, Disabled, Error state
- **Layout Components**: With different children, various spacing
- **Accordions/Tabs**: Open/Closed, Multiple items, Keyboard navigation

### Organisms (Complex Components)

**Characteristics**:
- Complex state management
- Multiple sub-components
- May require global store (AppStoreProvider)
- Need mock data and decorators

**Recommended Story Count**: 3-6 stories per organism

**Pattern 1: With Mock Data**
```typescript
import type { Meta as StoryMeta, StoryObj } from '@storybook/react-vite'
import type { JSX } from 'react'

import { SessionControl } from '../index'

// Mock data generation
const generateMockSession = () => ({
  id: '123',
  purpose: 'Test session',
  created_at: new Date().toISOString()
})

const Meta = {
  title: 'Organisms/SessionControl',
  component: SessionControl,
  tags: ['autodocs']
} satisfies StoryMeta<typeof SessionControl>

export default Meta
type Story = StoryObj<typeof Meta>

export const Default: Story = {
  args: {
    session: generateMockSession()
  }
}
```

**Pattern 2: With Store Provider**
```typescript
import type { Decorator } from '@storybook/react-vite'
import { AppStoreProvider } from '@/stores/useAppStore'

// Decorator for organisms that need global state
const withAppStore: Decorator = (Story) => (
  <AppStoreProvider>
    <Story />
  </AppStoreProvider>
)

const Meta = {
  title: 'Organisms/Form',
  decorators: [withAppStore],
  tags: ['autodocs']
} satisfies StoryMeta<unknown>

export default Meta
type Story = StoryObj<typeof Meta>
```

**Pattern 3: Interactive Scenarios**
```typescript
export const WithValidation: Story = {
  render: (): JSX.Element => {
    const ValidationExample = (): JSX.Element => {
      const InnerForm = (): JSX.Element => {
        const methods = useFormContext()

        return (
          <div style={{ display: 'grid', gap: 8 }}>
            <Fieldset legend="Email">
              {(ids) => (
                <InputText
                  name="email"
                  type="email"
                  placeholder="email@example.com"
                  register={methods.register}
                  aria-describedby={[ids.hintId, ids.errorId]
                    .filter(Boolean)
                    .join(' ')}
                  aria-required={true}
                />
              )}
            </Fieldset>

            <Button type="submit">Submit</Button>
          </div>
        )
      }

      const schema = z.object({
        email: z.string().email('Valid email is required')
      })

      return (
        <Form schema={schema} defaultValues={{ email: '' }}>
          <InnerForm />
        </Form>
      )
    }

    return <ValidationExample />
  }
}
```

**Organisms Example Variants**:
- **Forms**: Default, With validation errors, Submitting state, Success state
- **Data Display**: Empty state, Loading, With data, Error state
- **Interactive Components**: Default interaction, Keyboard navigation, Edge cases

## Common Patterns

### ARIA Attributes

Always include accessibility attributes in stories:

```typescript
export const Accessible: Story = {
  args: {
    'aria-label': 'Descriptive label',
    'aria-describedby': 'help-text',
    'aria-required': true,
    'aria-invalid': false
  }
}
```

### Error States

Show error handling in stories:

```typescript
export const WithError: Story = {
  args: {
    error: 'This field is required',
    'aria-invalid': true
  }
}
```

### Loading States

Demonstrate loading behavior:

```typescript
export const Loading: Story = {
  args: {
    isLoading: true,
    'aria-busy': true
  }
}
```

### Disabled States

Show disabled variations:

```typescript
export const Disabled: Story = {
  args: {
    disabled: true,
    'aria-disabled': true
  }
}
```

## Styling in Stories

### Inline Styles (Use Sparingly)

**Rule**: Avoid inline styles in production code (see `roles/typescript/typescript.md`).

**Exception**: Inline styles are acceptable in Storybook stories for demonstration purposes.

```typescript
// ACCEPTABLE in stories
export const WithLayout: Story = {
  render: (): JSX.Element => (
    <div style={{ padding: 12, border: '1px solid #eee' }}>
      <Component />
    </div>
  )
}

// BETTER: Use component's own styling system when possible
export const Default: Story = {
  args: {
    className: styles.container
  }
}
```

## Story Naming Conventions

1. **Default**: The most common/basic usage
2. **Controlled**: Demonstrates controlled component pattern
3. **WithRHF**: React Hook Form integration
4. **Disabled**: Disabled state
5. **Loading**: Loading state
6. **WithError**: Error state
7. **[Variant]**: Specific variants (Primary, Secondary, Large, Small, etc.)

## Testing Coverage Guidelines

Based on `ts_test_strategist` recommendations:

### Atoms
- **Minimum**: 2 stories (Default + one variant)
- **Recommended**: 3-4 stories (Default + variants + states)

### Molecules
- **Minimum**: 3 stories (Default + Controlled + WithRHF for form elements)
- **Recommended**: 4-5 stories (add Disabled, Error states)

### Organisms
- **Minimum**: 3 stories (Default + key interaction + error state)
- **Recommended**: 4-6 stories based on complexity
- Use `ts_test_strategist` to calculate recommended story count

**Formula** (from `ts_test_strategist`):
```
If component has branches (conditional rendering):
  recommended_stories = max(3, branch_count + 1)
Else:
  recommended_stories = max(2, min(complexity + 1, 5))
```

## TypeScript Patterns

### Type Imports

Always use `type` imports for types:

```typescript
import type { Meta as StoryMeta, StoryObj } from '@storybook/react-vite'
import type { JSX } from 'react'
```

### Props Types

Use `typeof` to infer component props:

```typescript
type Story = StoryObj<typeof Meta>

// Or for complex components
type ComponentProps = ComponentType<typeof MyComponent>
```

## React Hook Form Integration

### Pattern 1: Using Form Provider

```typescript
import { Form, useFormContext } from '@/components/organisms/Form'
import { z } from 'zod'

export const WithValidation: Story = {
  render: (): JSX.Element => {
    const InnerForm = (): JSX.Element => {
      const methods = useFormContext()

      return (
        <InputText
          name="email"
          register={methods.register}
          aria-label="Email"
        />
      )
    }

    const schema = z.object({
      email: z.string().email()
    })

    return (
      <Form schema={schema} defaultValues={{ email: '' }}>
        <InnerForm />
      </Form>
    )
  }
}
```

### Pattern 2: Using Fieldset

```typescript
import { Fieldset } from '@/components/molecules/Fieldset'

export const WithFieldset: Story = {
  render: (): JSX.Element => {
    const InnerForm = (): JSX.Element => {
      const methods = useFormContext()

      return (
        <Fieldset legend="Email" hint="Enter your email">
          {(ids) => (
            <InputText
              name="email"
              register={methods.register}
              aria-describedby={[ids.hintId, ids.errorId]
                .filter(Boolean)
                .join(' ')}
            />
          )}
        </Fieldset>
      )
    }

    return (
      <Form schema={schema} defaultValues={{}}>
        <InnerForm />
      </Form>
    )
  }
}
```

## Prohibited Patterns

### ❌ Don't: Import Zod in Stories

```typescript
// ❌ BAD: Inline Zod schema
import { z } from 'zod'
const schema = z.object({ name: z.string() })
```

**Exception**: Zod imports are allowed in stories for demonstration purposes only (not production code).

### ❌ Don't: Use Real API Calls

```typescript
// ❌ BAD: Real API call
const data = await fetch('/api/sessions')

// ✅ GOOD: Mock data
const data = generateMockSession()
```

### ❌ Don't: Access Stores from Molecules/Atoms

```typescript
// ❌ BAD: Atom accessing store
import { useAppStore } from '@/stores/useAppStore'

const MyAtom = () => {
  const { pushToast } = useAppStore()  // FORBIDDEN
}

// ✅ GOOD: Receive callbacks via props
const MyAtom = ({ onError }) => {
  onError?.('Error message')
}
```

## References

- **Main TypeScript Guidelines**: `@roles/typescript/typescript.md`
- **Component Patterns**: `@roles/typescript/components/components.md`
- **Atoms**: `@roles/typescript/components/atoms.md`
- **Molecules**: `@roles/typescript/components/molecules.md`
- **Organisms**: `@roles/typescript/components/organisms.md`
- **React Hook Form**: `@roles/typescript/rhf.md`

## Summary

This role defines the technical **HOW** of creating Storybook stories:

1. **Structure**: Use TypeScript's `Meta` and `StoryObj` types
2. **Patterns**: Follow layer-specific patterns (atoms, molecules, organisms)
3. **Coverage**: Create 2-6 stories per component based on complexity
4. **Accessibility**: Always include ARIA attributes
5. **Integration**: Demonstrate React Hook Form usage for form components
6. **Type Safety**: Use TypeScript's type system throughout

For the **WHAT** (when to create stories, workflow steps), see `@procedures/typescript/tests/storybook.md`.
