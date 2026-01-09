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

## Play Functions (Interaction Testing)

### Overview

Play functions enable automated interaction testing within Storybook stories. They simulate user interactions and verify component behavior using `@storybook/testing-library` and `@storybook/jest`.

**When to Use Play Functions**:
- Testing user interactions (clicks, typing, focus)
- Verifying accessibility attributes
- Testing state changes and side effects
- Ensuring proper event handling

### Required Dependencies

For Storybook 10.x with Vitest integration:

```json
{
  "devDependencies": {
    "@storybook/addon-vitest": "^10.0.6",
    "storybook": "^10.0.6"
  }
}
```

**Note**: The `storybook` package includes the `storybook/test` module which provides all testing utilities (`expect`, `userEvent`, `within`, etc.).

### Basic Play Function Pattern

**IMPORTANT**: When using Storybook 10 with `@storybook/addon-vitest`, you MUST use `storybook/test` instead of `@storybook/jest` and `@storybook/testing-library`:

```typescript
import type { Meta as StoryMeta, StoryObj } from '@storybook/react-vite'
import { expect, userEvent, within } from 'storybook/test'

import { Button } from '../index'

const Meta = {
  title: 'Atoms/Button',
  component: Button,
  tags: ['autodocs']
} satisfies StoryMeta<typeof Button>

export default Meta
type Story = StoryObj<typeof Meta>

export const Default: Story = {
  args: {
    children: 'Click me'
  },
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement)
    const button = canvas.getByRole('button', { name: /click me/i })

    await expect(button).toBeInTheDocument()
    await userEvent.click(button)
  }
}
```

### Play Function Patterns by Use Case

#### Pattern 1: Click Interaction

```typescript
import { expect, fn, userEvent, within } from 'storybook/test'

export const ClickInteraction: Story = {
  args: {
    children: 'Primary Button',
    onClick: fn() // Use fn() from storybook/test for action tracking
  },
  play: async ({ canvasElement, args }) => {
    const canvas = within(canvasElement)
    const button = canvas.getByRole('button', { name: /primary button/i })

    await expect(button).toBeInTheDocument()
    await userEvent.click(button)
    await expect(args.onClick).toHaveBeenCalledTimes(1)
  }
}
```

#### Pattern 2: Accessibility Verification

```typescript
export const AccessibilityCheck: Story = {
  args: {
    children: 'Close',
    'aria-label': 'Close dialog'
  },
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement)
    const button = canvas.getByRole('button', { name: /close dialog/i })

    await expect(button).toBeInTheDocument()
    await expect(button).toHaveAccessibleName('Close dialog')
    await userEvent.click(button)
  }
}
```

#### Pattern 3: Disabled State Verification

```typescript
export const DisabledState: Story = {
  args: {
    disabled: true,
    children: 'Disabled Button',
    'aria-disabled': true
  },
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement)
    const button = canvas.getByRole('button', { name: /disabled button/i })

    await expect(button).toBeDisabled()
    await expect(button).toHaveAttribute('aria-disabled', 'true')
  }
}
```

#### Pattern 4: Form Input Testing

```typescript
export const FormInput: Story = {
  args: {
    placeholder: 'Enter your name',
    name: 'username',
    'aria-label': 'Username'
  },
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement)
    const input = canvas.getByRole('textbox', { name: /username/i })

    await expect(input).toBeInTheDocument()
    await userEvent.type(input, 'John Doe')
    await expect(input).toHaveValue('John Doe')
  }
}
```

#### Pattern 5: Multiple Interactions

```typescript
export const MultipleInteractions: Story = {
  render: (): JSX.Element => {
    const Example = (): JSX.Element => {
      const [count, setCount] = useState(0)

      return (
        <div>
          <button onClick={() => setCount(count + 1)}>
            Count: {count}
          </button>
        </div>
      )
    }

    return <Example />
  },
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement)
    const button = canvas.getByRole('button', { name: /count: 0/i })

    await userEvent.click(button)
    await expect(canvas.getByText(/count: 1/i)).toBeInTheDocument()

    await userEvent.click(button)
    await expect(canvas.getByText(/count: 2/i)).toBeInTheDocument()
  }
}
```

### Common Testing Utilities

#### Finding Elements

```typescript
// By role (preferred for accessibility)
const button = canvas.getByRole('button', { name: /submit/i })
const textbox = canvas.getByRole('textbox', { name: /email/i })
const checkbox = canvas.getByRole('checkbox', { name: /agree/i })

// By label text
const input = canvas.getByLabelText(/username/i)

// By text content
const heading = canvas.getByText(/welcome/i)

// By placeholder
const input = canvas.getByPlaceholderText(/enter email/i)
```

#### User Events

```typescript
// Click
await userEvent.click(element)

// Type text
await userEvent.type(input, 'Hello world')

// Clear and type
await userEvent.clear(input)
await userEvent.type(input, 'New text')

// Keyboard events
await userEvent.keyboard('{Enter}')
await userEvent.keyboard('{Tab}')

// Hover
await userEvent.hover(element)
await userEvent.unhover(element)
```

#### Assertions

```typescript
// Presence
await expect(element).toBeInTheDocument()
await expect(element).not.toBeInTheDocument()

// Visibility
await expect(element).toBeVisible()
await expect(element).not.toBeVisible()

// State
await expect(button).toBeDisabled()
await expect(button).toBeEnabled()
await expect(checkbox).toBeChecked()

// Attributes
await expect(element).toHaveAttribute('aria-label', 'Close')
await expect(element).toHaveAccessibleName('Submit form')
await expect(input).toHaveValue('test value')

// Text content
await expect(element).toHaveTextContent('Hello')

// CSS classes (avoid with CSS modules)
// Note: Don't use toHaveClass with vanilla-extract or CSS modules
// as class names are dynamically generated
```

### Best Practices

1. **Use Semantic Queries**: Prefer `getByRole` over `getByTestId` for better accessibility testing
2. **Async/Await**: Always use `await` with user events and assertions
3. **Regex Patterns**: Use case-insensitive regex for text matching: `/submit/i`
4. **Avoid CSS Class Checks**: Don't test dynamically generated CSS module classes
5. **Test User Behavior**: Focus on testing what users see and do, not implementation details
6. **Keep Tests Simple**: Each play function should test one primary interaction or scenario

### Layer-Specific Recommendations

#### Atoms
- Test basic interactions (click, focus, blur)
- Verify accessibility attributes
- Test disabled/enabled states
- **Example count**: 2-4 play functions per component

#### Molecules
- Test form input interactions
- Verify controlled/uncontrolled behavior
- Test validation feedback
- **Example count**: 3-5 play functions per component

#### Organisms
- Test complex user workflows
- Verify multi-step interactions
- Test error handling and recovery
- **Example count**: 4-6 play functions per component

### Important Notes for Storybook 10 + Vitest

#### Correct Import Pattern

When using `@storybook/addon-vitest` with Storybook 10.x, **always import from `storybook/test`**:

```typescript
// ✅ CORRECT: Storybook 10 with addon-vitest
import { expect, userEvent, within, fn } from 'storybook/test'

// ❌ WRONG: These will cause import errors in Vitest browser mode
import { expect } from '@storybook/jest'
import { userEvent, within } from '@storybook/testing-library'
```

**Why?** The `storybook/test` module is specifically designed to work with Vitest and provides:
- Async-compatible `expect` assertions (based on Vitest's expect)
- Testing Library utilities (`userEvent`, `within`)
- Mock function utilities (`fn`, `spyOn`)
- Full compatibility with `@storybook/addon-vitest`

#### Error: "BrowserTestRunner.importFile failed"

If you see this error when running Vitest with Storybook stories:

```
Error:
    at BrowserTestRunner.importFile
```

**Cause**: Using incompatible imports (`@storybook/jest` or `@storybook/testing-library`) with Vitest browser mode.

**Solution**: Change all imports to use `storybook/test`:

```typescript
// Before (causes error)
import { expect } from '@storybook/jest'
import { userEvent, within } from '@storybook/testing-library'

// After (works correctly)
import { expect, userEvent, within } from 'storybook/test'
```

### Troubleshooting

#### Issue: Tests fail in Docker

**Solution**: Install Playwright browsers in Dockerfile

```dockerfile
# Install Playwright system dependencies and browsers
RUN npx playwright install-deps && \
    npx playwright install
```

#### Issue: Element not found

**Solution**: Use `findBy*` queries for asynchronous elements

```typescript
// Instead of getBy (synchronous)
const button = canvas.getByRole('button')

// Use findBy for async elements
const button = await canvas.findByRole('button')
```

#### Issue: CSS class name mismatch

**Solution**: Avoid testing CSS classes with vanilla-extract/CSS modules. Test behavior instead.

```typescript
// ❌ BAD: Testing generated class names
await expect(button).toHaveClass('secondary')

// ✅ GOOD: Test behavior or attributes
await expect(button).toBeInTheDocument()
await userEvent.click(button)
```

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

## Common Pitfalls and Solutions

### Issue 1: Form Validation Not Triggering

**Problem**: Error messages don't appear when using React Hook Form validation in stories.

**Cause**: React Hook Form's default validation mode is `onSubmit`, which doesn't trigger on blur events.

**Solution**: Explicitly set `mode="onBlur"` on the `Form` component to trigger validation when input loses focus.

```typescript
// ❌ BAD: Validation won't trigger on blur
export const WithError: Story = {
  render: (args): JSX.Element => {
    const schema = z.object({
      [args.name]: z.string().min(1, 'This field is required')
    })

    return (
      <Form schema={schema} defaultValues={{ [args.name]: '' }}>
        <InputField {...args} />
      </Form>
    )
  },
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement)
    const input = canvas.getByRole('textbox')

    await userEvent.type(input, 'test')
    await userEvent.clear(input)
    await userEvent.tab()

    // ❌ This will fail - error message won't appear
    const error = await canvas.findByText(/this field is required/i)
    await expect(error).toBeInTheDocument()
  }
}

// ✅ GOOD: Add mode="onBlur" to trigger validation
export const WithError: Story = {
  render: (args): JSX.Element => {
    const schema = z.object({
      [args.name]: z.string().min(1, 'This field is required')
    })

    return (
      <Form schema={schema} defaultValues={{ [args.name]: '' }} mode="onBlur">
        <InputField {...args} />
      </Form>
    )
  },
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement)
    const input = canvas.getByRole('textbox')

    await userEvent.type(input, 'test')
    await userEvent.clear(input)
    await userEvent.tab()

    // ✅ Error message will appear after blur
    const error = await canvas.findByText(/this field is required/i)
    await expect(error).toBeInTheDocument()
  }
}
```

**Available validation modes**:
- `onBlur`: Validates when field loses focus (recommended for real-time feedback)
- `onChange`: Validates on every keystroke (can be too aggressive)
- `onSubmit`: Validates only on form submission (default)
- `onTouched`: Validates after first blur, then on every change

### Issue 2: Nested Forms Breaking Submit Events

**Problem**: `onSubmit` callback not being called when testing form submission.

**Cause**: HTML doesn't allow nested `<form>` elements. Some components like `InputSearch` have their own `<form>` wrapper. When placed inside another `Form` component, the nested form's `event.preventDefault()` blocks the outer form's submission.

**Solution**: Don't nest forms. Components with their own `<form>` elements should be placed outside the `Form` component or tested independently.

```typescript
// ❌ BAD: Nested forms - onSubmit won't be called
export const WithRHF: Story = {
  render: (args): JSX.Element => (
    <Form>
      {/* InputSearch has its own <form> element */}
      <InputSearch {...args} name="searchQuery" />
      <button type="submit">Submit Form</button>
    </Form>
  ),
  play: async ({ args, canvasElement }) => {
    const canvas = within(canvasElement)
    const submitButton = canvas.getByRole('button', { name: /submit form/i })
    await userEvent.click(submitButton)

    // ❌ This will fail - args.onSubmit was never called
    await expect(args.onSubmit).toHaveBeenCalled()
  }
}

// ✅ GOOD: Remove nested form, test component's own submit
export const WithRHF: Story = {
  render: (args): JSX.Element => (
    <div>
      <Form>
        <input name="otherField" placeholder="Other field" />
      </Form>
      {/* InputSearch outside of Form - uses its own form */}
      <InputSearch {...args} name="searchQuery" />
    </div>
  ),
  play: async ({ args, canvasElement }) => {
    const canvas = within(canvasElement)
    const input = canvas.getByRole('textbox', { name: /search/i })
    await userEvent.type(input, 'test')

    // Click the component's own submit button
    const submitButton = canvas.getByRole('button', { name: /search/i })
    await userEvent.click(submitButton)

    // ✅ args.onSubmit will be called correctly
    await expect(args.onSubmit).toHaveBeenCalled()
  }
}
```

**Components that have their own `<form>` element**:
- `InputSearch`: Has built-in form with submit button

**Rule of thumb**: If a component accepts an `onSubmit` prop and has its own `<form>`, don't wrap it in another `Form` component.

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
