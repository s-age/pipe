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
const switchElement = canvas.getByRole('switch', { name: /toggle/i })

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

// Switch state (use aria-checked, not toBeChecked)
await expect(switchElement).toHaveAttribute('aria-checked', 'true')
await expect(switchElement).toHaveAttribute('aria-checked', 'false')

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

#### Issue: "This interaction test passed in this browser, but the tests failed in the CLI"

**Problem**: Storybook shows warning "This interaction test passed in this browser, but the tests failed in the CLI" for stories that use `fn()` mock functions.

**Cause**: Using `fn()` to create mock callback functions without actually verifying those callbacks are called in the `play` function. This creates environment differences between browser and CLI test runners.

**Solution**: Always verify `fn()` mock functions are called in your `play` function, or use regular functions instead.

```typescript
// ❌ BAD: Using fn() without verification in play function
import { fn } from 'storybook/test'

const Meta = {
  component: MyComponent,
  args: {
    onChange: fn(),
    onFocus: fn()
  }
} satisfies StoryMeta<typeof MyComponent>

export const Default: Story = {
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement)
    const input = canvas.getByRole('textbox')

    await userEvent.type(input, 'test')
    // ❌ onChange callback created with fn() but never verified
  }
}

// ✅ GOOD: Verify fn() callbacks are called
import { expect, fn, userEvent, within } from 'storybook/test'

const Meta = {
  component: MyComponent,
  args: {
    onChange: fn(),
    onFocus: fn()
  }
} satisfies StoryMeta<typeof MyComponent>

export const Default: Story = {
  play: async ({ args, canvasElement }) => {
    const canvas = within(canvasElement)
    const input = canvas.getByRole('textbox')

    // Verify onFocus is called
    await userEvent.click(input)
    await expect(args.onFocus).toHaveBeenCalled()

    // Verify onChange is called
    await userEvent.type(input, 'test')
    await expect(args.onChange).toHaveBeenCalled()
  }
}

// ✅ ALTERNATIVE: Use regular functions if not testing callbacks
const Meta = {
  component: MyComponent,
  args: {
    onChange: (): void => {
      console.log('onChange called')
    },
    onFocus: (): void => {
      console.log('onFocus called')
    }
  }
} satisfies StoryMeta<typeof MyComponent>

export const Default: Story = {
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement)
    const input = canvas.getByRole('textbox')

    await userEvent.type(input, 'test')
    // No need to verify callbacks since we're not testing them
  }
}
```

**Key principle**: Only use `fn()` when you intend to verify the callback is called in your `play` function. Otherwise, use regular functions.

**Components commonly affected**:
- Form components with `onChange`, `onSubmit`, `onBlur` callbacks
- Interactive components with `onClick`, `onFocus`, `onHover` callbacks
- Components with `onRefresh`, `onClose`, `onConfirm` callbacks

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

### Issue 3: Callback Props Not Being Called in Controlled Stories

**Problem**: Testing callbacks like `onClose`, `onSubmit`, etc. in controlled component stories, but `args.onClose` is never called even though the component appears to work correctly.

**Cause**: The controlled story creates its own state and event handlers that bypass the `args` callback. When you click a button in the component's children, it only calls the local state setter, not the `args` callback that the test is monitoring.

**Solution**: Create a shared handler function that calls both the local state update AND the `args` callback. Use this handler consistently for all close/submit actions.

```typescript
// ❌ BAD: Local handler doesn't call args callback
export const Controlled: Story = {
  render: (args): JSX.Element => {
    const ControlledExample = (): JSX.Element => {
      const [isOpen, setIsOpen] = useState(false)

      return (
        <div>
          <button type="button" onClick={() => setIsOpen(true)}>
            Open Modal
          </button>
          <Modal
            {...args}
            isOpen={isOpen}
            onClose={() => {
              setIsOpen(false)
              args.onClose?.()  // Modal's onClose calls this
            }}
          >
            <div>
              <h2>Controlled Modal</h2>
              {/* ❌ This button only calls setIsOpen, not args.onClose */}
              <button type="button" onClick={() => setIsOpen(false)}>
                Close
              </button>
            </div>
          </Modal>
        </div>
      )
    }

    return <ControlledExample />
  },
  play: async ({ args, canvasElement }) => {
    const canvas = within(canvasElement)
    const openButton = canvas.getByRole('button', { name: /open modal/i })
    await userEvent.click(openButton)

    const modal = await canvas.findByRole('dialog')
    const closeButton = within(modal).getByRole('button', { name: /close/i })
    await userEvent.click(closeButton)

    // ❌ This will fail - args.onClose was never called
    await expect(args.onClose).toHaveBeenCalled()
  }
}

// ✅ GOOD: Shared handler calls both state setter and args callback
export const Controlled: Story = {
  render: (args): JSX.Element => {
    const ControlledExample = (): JSX.Element => {
      const [isOpen, setIsOpen] = useState(false)

      // ✅ Single handler that calls both
      const handleClose = (): void => {
        setIsOpen(false)
        args.onClose?.()
      }

      return (
        <div>
          <button type="button" onClick={() => setIsOpen(true)}>
            Open Modal
          </button>
          <Modal
            {...args}
            isOpen={isOpen}
            onClose={handleClose}  // ✅ Use shared handler
          >
            <div>
              <h2>Controlled Modal</h2>
              {/* ✅ Button also uses shared handler */}
              <button type="button" onClick={handleClose}>
                Close
              </button>
            </div>
          </Modal>
        </div>
      )
    }

    return <ControlledExample />
  },
  play: async ({ args, canvasElement }) => {
    const canvas = within(canvasElement)
    const openButton = canvas.getByRole('button', { name: /open modal/i })
    await userEvent.click(openButton)

    const modal = await canvas.findByRole('dialog')
    const closeButton = within(modal).getByRole('button', { name: /close/i })
    await userEvent.click(closeButton)

    // ✅ args.onClose will be called correctly
    await expect(args.onClose).toHaveBeenCalled()
  }
}
```

**Key principle**: In controlled stories, any action that should trigger a callback prop must use a handler that calls both:
1. The local state update (e.g., `setIsOpen(false)`)
2. The args callback (e.g., `args.onClose?.()`)

**Common callbacks this applies to**:
- `onClose`: Modal, Dialog, Drawer components
- `onSubmit`: Form components
- `onChange`: Input components
- `onConfirm`, `onCancel`: Confirmation dialogs

### Issue 4: "Found multiple elements" with getByText

**Problem**: Test fails with error "Found multiple elements with the text: Apple" when using `getByText` to find options in Select/MultipleSelect components.

**Cause**: Components with hidden native `<select>` elements render the same text twice:
1. In the hidden `<select><option>` for form compatibility
2. In the visible custom dropdown UI

When you use `canvas.getByText('Apple')`, Testing Library finds both elements and throws an error because the query must return exactly one element.

**Solution**: Use `getByRole('option')` scoped to the visible listbox instead of `getByText`.

```typescript
// ❌ BAD: getByText finds both hidden and visible elements
export const Default: Story = {
  args: {
    options: ['Apple', 'Banana', 'Cherry'],
    placeholder: 'Choose a fruit'
  },
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement)
    const trigger = canvas.getByRole('button')
    await userEvent.click(trigger)

    // ❌ Error: Found multiple elements with the text: Apple
    await expect(canvas.getByText('Apple')).toBeInTheDocument()
  }
}

// ✅ GOOD: Use getByRole('option') scoped to listbox
export const Default: Story = {
  args: {
    options: ['Apple', 'Banana', 'Cherry'],
    placeholder: 'Choose a fruit'
  },
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement)
    const trigger = canvas.getByRole('button', { name: /choose a fruit/i })
    await userEvent.click(trigger)

    const listbox = await canvas.findByRole('listbox')
    const options = within(listbox).getAllByRole('option')
    await expect(options).toHaveLength(3)
    await expect(options[0]).toHaveTextContent('Apple')
  }
}

// ✅ GOOD: For single option selection
export const Controlled: Story = {
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement)
    const trigger = canvas.getByRole('button')
    await userEvent.click(trigger)

    const listbox = await canvas.findByRole('listbox')
    const option = within(listbox).getByRole('option', { name: /apple/i })
    await userEvent.click(option)
  }
}
```

**Key principles**:
- Always scope option queries to the `listbox`: `within(listbox).getByRole('option')`
- Use `getAllByRole('option')` for multiple options verification
- Use `getByRole('option', { name: /text/i })` for single option selection
- Never use `getByText` for option elements in Select/MultipleSelect components

**Components affected**:
- `Select`: Has hidden `<select>` (index.tsx:105-118) and visible dropdown (index.tsx:158-184)
- `MultipleSelect`: Has hidden `<select multiple>` and visible dropdown

### Issue 5: Field Components Require Form Context

**Problem**: Test fails with "Cannot read properties of null (reading 'control')" when using Field components (e.g., `InputField`, `TextareaField`, `SelectField`) without a Form wrapper.

**Cause**: Field components use React Hook Form's `useController` hook, which requires a form context. They cannot be used standalone - they must always be wrapped in a `Form` component.

**Solution**: Always wrap Field components in a `Form` component, even in the Default story.

```typescript
// ❌ BAD: Field component without Form wrapper
export const Default: Story = {
  args: {
    id: 'input-field',
    label: 'Label',
    name: 'testField',
    placeholder: 'Placeholder text'
  }
}

// ✅ GOOD: Wrap in Form component
export const Default: Story = {
  render: (args): JSX.Element => (
    <Form defaultValues={{ [args.name]: '' }}>
      <InputField {...args} />
    </Form>
  )
}

// ✅ GOOD: With initial value
export const WithValue: Story = {
  render: (args): JSX.Element => (
    <Form defaultValues={{ [args.name]: 'Initial value' }}>
      <InputField {...args} />
    </Form>
  )
}

// ✅ GOOD: With validation
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
  }
}
```

**Key principles**:
- **Always** wrap Field components in `Form`, even for simple stories
- Use `defaultValues` to set initial values instead of component props
- Field components include any component that uses `useController`:
  - `InputField`
  - `TextareaField`
  - `SelectField`
  - `CheckboxField`
  - Any custom field component using `useController`

**Components that DON'T need Form wrapper**:
- Base input components: `InputText`, `TextArea`, `Select`, `Checkbox`
- These components can be used standalone or with `register` prop

**Rule of thumb**: If the component name ends with "Field", it needs a `Form` wrapper.

### Issue 6: Range Input onChange Not Triggering with userEvent.type

**Problem**: Test fails with "expected 'onChange' to be called at least once" when testing Slider or range input components using `userEvent.type()` for keyboard interactions.

**Cause**: `userEvent.type()` is designed for text input fields and doesn't properly trigger change events on `<input type="range">` elements. Keyboard navigation on range inputs requires actual key events, not character typing.

**Solution**: Use `fireEvent.change()` directly to change slider values in tests instead of simulating keyboard interactions.

```typescript
// ❌ BAD: Using userEvent.type() with range input
import { expect, fn, userEvent, within } from 'storybook/test'

export const Controlled: Story = {
  args: {
    onChange: fn()
  },
  play: async ({ args, canvasElement }) => {
    const canvas = within(canvasElement)
    const slider = canvas.getByRole('slider')

    // ❌ This doesn't work for range inputs
    await userEvent.type(slider, '{ArrowRight}')
    await expect(args.onChange).toHaveBeenCalled()
  }
}

// ❌ BAD: Using userEvent.click() + userEvent.keyboard()
export const Controlled: Story = {
  args: {
    onChange: fn()
  },
  play: async ({ args, canvasElement }) => {
    const canvas = within(canvasElement)
    const slider = canvas.getByRole('slider')

    // ❌ This also doesn't reliably work
    await userEvent.click(slider)
    await userEvent.keyboard('{ArrowRight}')
    await expect(args.onChange).toHaveBeenCalled()
  }
}

// ❌ BAD: Trying to simulate pointer drag
export const Controlled: Story = {
  args: {
    onChange: fn()
  },
  play: async ({ args, canvasElement }) => {
    const canvas = within(canvasElement)
    const slider = canvas.getByRole('slider')

    // ❌ Complex and unreliable for range inputs
    const sliderRect = slider.getBoundingClientRect()
    const startX = sliderRect.left + sliderRect.width * 0.3
    const endX = sliderRect.left + sliderRect.width * 0.5
    const centerY = sliderRect.top + sliderRect.height / 2

    await userEvent.pointer([
      { keys: '[MouseLeft>]', target: slider, coords: { x: startX, y: centerY } },
      { coords: { x: endX, y: centerY } },
      { keys: '[/MouseLeft]' }
    ])

    await expect(args.onChange).toHaveBeenCalled()
  }
}

// ✅ GOOD: Use fireEvent.change() directly
import { expect, fireEvent, fn, within } from 'storybook/test'

export const Controlled: Story = {
  args: {
    onChange: fn()
  },
  render: (args): JSX.Element => {
    const ControlledExample = (): JSX.Element => {
      const [value, setValue] = useState(30)

      const handleChange = (v: number): void => {
        setValue(v)
        args.onChange?.(v)
      }

      return (
        <div style={{ width: 360 }}>
          <Slider {...args} value={value} onChange={handleChange} />
          <div style={{ marginTop: 16 }}>Current Value: {value}</div>
        </div>
      )
    }

    return <ControlledExample />
  },
  play: async ({ args, canvasElement }) => {
    const canvas = within(canvasElement)
    const slider = canvas.getByRole('slider')

    // ✅ Directly change the value
    fireEvent.change(slider, { target: { value: '50' } })

    await expect(args.onChange).toHaveBeenCalled()
  }
}
```

**Key principles**:
- For range inputs (`<input type="range">`), use `fireEvent.change()` to test value changes
- `userEvent.type()` is for text inputs only
- Don't attempt complex pointer drag simulations for range inputs in tests
- Focus on testing the onChange callback is called, not simulating exact user interactions

**Components affected**:
- `Slider`: Uses `<input type="range">` underneath SVG visualization
- Any custom range input components

**Why fireEvent instead of userEvent?**
- `userEvent` attempts to simulate realistic user interactions, but range input interactions are complex (drag, click-to-position, keyboard navigation)
- `fireEvent.change()` directly triggers the change event, which is what we actually want to test
- Testing that `onChange` is called is more important than simulating exact user gestures

### Issue 7: Switch Components Require role="switch" Not role="checkbox"

**Problem**: Test fails with "Unable to find an accessible element with the role 'checkbox'" when testing toggle switch components, even though a checkbox input exists in the DOM.

**Cause**: Toggle switch components that use `<label>` with `onClick` to handle toggle events (instead of relying on the native checkbox click) need to expose themselves as `role="switch"` to screen readers and testing tools. The internal `<input type="checkbox">` should be hidden from the accessibility tree with `aria-hidden="true"` since the parent label handles all interactions.

**Why this pattern exists**:
- Native checkboxes have `event.stopPropagation()` in their click handlers to prevent double-firing
- This means clicking the checkbox directly won't trigger the parent label's onClick handler
- The component intentionally uses label-level onClick for all toggle interactions
- Therefore, the checkbox is a visual/form element only, not the interactive element

**Solution**: Implement proper WAI-ARIA switch pattern with `role="switch"`, `aria-checked`, and keyboard support.

```typescript
// ❌ BAD: Checkbox-based implementation without proper ARIA
export const ToggleSwitch = ({ checked, onChange }): JSX.Element => {
  return (
    <label onClick={() => onChange(!checked)}>
      <input
        type="checkbox"
        checked={checked}
        onChange={() => {}} // Empty handler, label handles toggle
      />
      <span>Toggle</span>
    </label>
  )
}

// Test fails trying to find checkbox
export const Interaction: Story = {
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement)
    // ❌ Checkbox exists but isn't the interactive element
    const toggle = canvas.getByRole('checkbox') // Error!
    await userEvent.click(toggle) // Click won't trigger onChange
  }
}

// ✅ GOOD: Proper WAI-ARIA switch implementation
export const ToggleSwitch = ({
  checked,
  onChange,
  ariaLabel
}): JSX.Element => {
  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === ' ' || e.key === 'Enter') {
      e.preventDefault()
      onChange(!checked)
    }
  }

  return (
    <label
      role="switch"
      aria-checked={checked}
      aria-label={ariaLabel}
      tabIndex={0}
      onClick={() => onChange(!checked)}
      onKeyDown={handleKeyDown}
    >
      <input
        type="checkbox"
        checked={checked}
        aria-hidden="true"
        tabIndex={-1}
        onChange={() => {}}
      />
      <span>Toggle</span>
    </label>
  )
}

// Test uses role="switch" and checks aria-checked
export const Interaction: Story = {
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement)
    const toggle = canvas.getByRole('switch', { name: /toggle/i })

    // Initial state
    await expect(toggle).toHaveAttribute('aria-checked', 'false')

    // Click to toggle
    await userEvent.click(toggle)
    await expect(toggle).toHaveAttribute('aria-checked', 'true')
  }
}
```

**Required ARIA attributes for switch pattern**:
- `role="switch"` - Identifies element as a switch
- `aria-checked="true|false"` - Current state (use boolean converted to string)
- `aria-label` or `aria-labelledby` - Accessible name
- `tabIndex={0}` - Keyboard focusable (or -1 if disabled)
- `onKeyDown` handler - Support Space and Enter keys

**Internal checkbox attributes**:
- `aria-hidden="true"` - Hide from accessibility tree
- `tabIndex={-1}` - Remove from keyboard navigation
- Keep `checked` synced for form compatibility
- Use `onChange={() => {}}` to satisfy React controlled component

**Key principles**:
- Don't use `toBeChecked()` for switch elements - it checks the internal checkbox, not the switch state
- Use `toHaveAttribute('aria-checked', 'true')` to verify switch state
- Always implement keyboard support (Space/Enter) for switches
- The switch role requires aria-checked, not the checked HTML attribute

**Components affected**:
- Toggle switches
- ON/OFF controls
- Enable/disable toggles
- Any checkbox-styled control that uses label-level onClick

**References**:
- [WAI-ARIA Switch Pattern](https://www.w3.org/WAI/ARIA/apg/patterns/switch/)
- [MDN: role="switch"](https://developer.mozilla.org/en-US/docs/Web/Accessibility/ARIA/Roles/switch_role)

### Issue 8: Async Callbacks Not Called Before Assertion

**Problem**: Test fails with "expected 'refreshSessions' to be called at least once" even though the user interaction appears to work correctly in the browser.

**Cause**: The component's event handler performs asynchronous operations (API calls) before calling the callback prop. The test assertion runs immediately after `userEvent.click()`, before the async work completes.

**Common scenario**:
```typescript
// Component handler
const handleToggle = async () => {
  await apiCall()  // Async operation
  await refreshSessions()  // Callback called AFTER async work
}
```

**Solution**: Use `waitFor()` to wait for the async callback to be called.

```typescript
// ❌ BAD: Immediate assertion after user event
import { expect, fn, userEvent, within } from 'storybook/test'

export const Interaction: Story = {
  args: {
    onRefresh: fn()
  },
  play: async ({ args, canvasElement }) => {
    const canvas = within(canvasElement)
    const button = canvas.getByRole('button')

    await userEvent.click(button)
    // ❌ Fails - onRefresh hasn't been called yet
    await expect(args.onRefresh).toHaveBeenCalled()
  }
}

// ✅ GOOD: Wait for async callback
import { expect, fn, userEvent, waitFor, within } from 'storybook/test'

export const Interaction: Story = {
  args: {
    onRefresh: fn()
  },
  play: async ({ args, canvasElement }) => {
    const canvas = within(canvasElement)
    const button = canvas.getByRole('button')

    await userEvent.click(button)
    // ✅ Waits up to 1000ms for callback to be called
    await waitFor(() => expect(args.onRefresh).toHaveBeenCalled())
  }
}

// ✅ GOOD: With custom timeout for slow operations
export const SlowOperation: Story = {
  args: {
    onRefresh: fn()
  },
  play: async ({ args, canvasElement }) => {
    const canvas = within(canvasElement)
    const button = canvas.getByRole('button')

    await userEvent.click(button)
    // Wait up to 3 seconds for slow API calls
    await waitFor(() => expect(args.onRefresh).toHaveBeenCalled(), {
      timeout: 3000
    })
  }
}
```

**Key principles**:
- Always use `waitFor()` when testing callbacks that are called after async operations
- Default timeout is 1000ms, increase for slow operations
- `waitFor()` polls the assertion until it passes or times out
- Don't assume callbacks are called synchronously, even with `await userEvent.click()`

**When to use `waitFor()` for callbacks**:
- Callbacks called after API requests (fetch, axios)
- Callbacks in components with debounced handlers
- Callbacks that depend on state updates completing
- Any callback not called synchronously in the event handler

**Components commonly affected**:
- Components with `onRefresh`, `onSave`, `onSubmit` after API calls
- Components with debounced `onChange` handlers
- Components that update server state before calling callbacks

**Timeout guidelines**:
- Default (1000ms): Most API calls with MSW mocks
- 2000-3000ms: Debounced inputs, slower operations
- 5000ms+: Only for intentionally slow operations (avoid if possible)

### Issue 9: Async State Updates Not Completing Before Assertion

**Problem**: Test fails with "Unable to find an element with the text: Selected: Green" even though the element should exist after user interaction.

**Cause**: After clicking an option in a controlled component, multiple asynchronous operations occur:
1. User clicks option
2. `onChange` event fires and updates React state
3. Dropdown closes
4. React re-renders with new state
5. DOM updates with new value

If you use synchronous queries (`getByText`) immediately after `userEvent.click()`, the test runs before steps 3-5 complete.

**Solution**: Use `findByText` (async query) and wait for the dropdown to close before asserting the result.

```typescript
// ❌ BAD: Using getByText immediately after click
export const Controlled: Story = {
  render: (args): JSX.Element => {
    const ControlledExample = (): JSX.Element => {
      const [value, setValue] = useState<string | undefined>(undefined)

      return (
        <div>
          <Select
            {...args}
            value={value}
            onChange={(e) => setValue(e.target.value)}
          />
          <div>Selected: {value ?? 'None'}</div>
        </div>
      )
    }

    return <ControlledExample />
  },
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement)
    const trigger = canvas.getByRole('button')
    await userEvent.click(trigger)

    const listbox = await canvas.findByRole('listbox')
    const option = within(listbox).getByRole('option', { name: /green/i })
    await userEvent.click(option)

    // ❌ Error: Unable to find element - state hasn't updated yet
    await expect(canvas.getByText('Selected: Green')).toBeInTheDocument()
  }
}

// ✅ GOOD: Wait for dropdown to close and use findByText
export const Controlled: Story = {
  render: (args): JSX.Element => {
    const ControlledExample = (): JSX.Element => {
      const [value, setValue] = useState<string | undefined>(undefined)

      return (
        <div>
          <Select
            {...args}
            value={value}
            onChange={(e) => setValue(e.target.value)}
          />
          <div>Selected: {value ?? 'None'}</div>
        </div>
      )
    }

    return <ControlledExample />
  },
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement)
    const trigger = canvas.getByRole('button', { name: /select a color/i })
    await userEvent.click(trigger)

    const listbox = await canvas.findByRole('listbox')
    const option = within(listbox).getByRole('option', { name: /green/i })
    await userEvent.click(option)

    // ✅ Wait for dropdown to close
    await expect(canvas.queryByRole('listbox')).not.toBeInTheDocument()

    // ✅ Use findByText to wait for async state update
    const selectedText = await canvas.findByText(/selected:/i)
    await expect(selectedText).toHaveTextContent('Selected: Green')
  }
}
```

**Key principles**:
- Always wait for the dropdown/modal to close after selection: `await expect(canvas.queryByRole('listbox')).not.toBeInTheDocument()`
- Use `findByText` (async) instead of `getByText` (sync) when asserting state changes after user interaction
- Use partial text matching (`/selected:/i`) then verify full content with `toHaveTextContent`
- Remember that `userEvent` actions are asynchronous even with `await` - the DOM updates come after

**When to use this pattern**:
- Controlled components with `useState` that update based on user interaction
- Any component where clicking triggers state changes that affect displayed text
- Components that close/hide after interaction (modals, dropdowns, tooltips)

## Mocking API Requests with MSW

### Overview

Stories that test components with API calls require mocking HTTP requests using MSW (Mock Service Worker). This allows components to behave realistically without making actual network requests.

### Setup

MSW is already configured in the Storybook environment:

1. **MSW Initialization** (`.storybook/preview.ts`):
   ```typescript
   import { initialize, mswLoader } from 'msw-storybook-addon'

   initialize()

   const preview: Preview = {
     loaders: [mswLoader]
   }
   ```

2. **Static Files** (`.storybook/main.ts`):
   ```typescript
   const config: StorybookConfig = {
     staticDirs: ['./public']  // Serves mockServiceWorker.js
   }
   ```

3. **Service Worker** (`.storybook/public/mockServiceWorker.js`):
   - Generated by `npx msw init .storybook/public`
   - Automatically loaded when Storybook starts

### Creating Mock Handlers

Mock handlers are organized by API resource in `src/web/msw/resources/`. Follow the [MSW Resources README](../../src/web/msw/resources/README.md) for file naming conventions.

**Example**: `src/web/msw/resources/fs.ts`

```typescript
import { http, HttpResponse } from 'msw'

import { API_BASE_URL } from '@/constants/uri'
import type { SessionSearchResponse } from '@/lib/api/fs/search'

/**
 * MSW handlers for /fs endpoints
 */
export const fsHandlers = [
  // POST /api/v1/fs/search
  http.post<never, { query: string }, SessionSearchResponse>(
    `${API_BASE_URL}/fs/search`,
    async ({ request }) => {
      const body = await request.json()
      const { query } = body

      // Return mock results
      return HttpResponse.json({
        results: [
          { sessionId: 'session-1', title: `${query} - Session 1` },
          { sessionId: 'session-2', title: `${query} - Session 2` }
        ]
      })
    }
  )
]
```

### Using Mock Handlers in Stories

Add MSW handlers to story parameters:

```typescript
import type { Meta as StoryMeta, StoryObj } from '@storybook/react-vite'
import { expect, userEvent, within } from 'storybook/test'

import { fsHandlers } from '@/msw/resources/fs'

import { SearchComponent } from '../index'

const Meta = {
  title: 'Organisms/SearchComponent',
  component: SearchComponent,
  tags: ['autodocs']
} satisfies StoryMeta<typeof SearchComponent>

export default Meta
type Story = StoryObj<typeof Meta>

/**
 * Demonstrates search with mocked API responses
 */
export const SearchInteraction: Story = {
  parameters: {
    msw: {
      handlers: fsHandlers  // Apply mock handlers
    }
  },
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement)
    const input = canvas.getByPlaceholderText(/search/i)

    // Type to trigger API call
    await userEvent.type(input, 'test')

    // Wait for API response and UI update
    const results = await canvas.findByText(/session-1/i)
    await expect(results).toBeInTheDocument()
  }
}
```

### Pattern: Override Handlers for Specific Stories

You can override or extend handlers for individual stories:

```typescript
import { http, HttpResponse } from 'msw'
import { API_BASE_URL } from '@/constants/uri'
import { fsHandlers } from '@/msw/resources/fs'

// Story with empty results
export const EmptyResults: Story = {
  parameters: {
    msw: {
      handlers: [
        // Override the search handler
        http.post(`${API_BASE_URL}/fs/search`, () => {
          return HttpResponse.json({ results: [] })
        })
      ]
    }
  },
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement)
    const input = canvas.getByPlaceholderText(/search/i)

    await userEvent.type(input, 'test')

    const noResults = await canvas.findByText(/no results/i)
    await expect(noResults).toBeInTheDocument()
  }
}

// Story with error response
export const ErrorState: Story = {
  parameters: {
    msw: {
      handlers: [
        http.post(`${API_BASE_URL}/fs/search`, () => {
          return HttpResponse.json(
            { message: 'Search service unavailable' },
            { status: 500 }
          )
        })
      ]
    }
  },
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement)
    const input = canvas.getByPlaceholderText(/search/i)

    await userEvent.type(input, 'test')

    const error = await canvas.findByText(/unavailable/i)
    await expect(error).toBeInTheDocument()
  }
}
```

### Pattern: Testing Debounced API Calls

When testing components with debounced API calls, use `findBy*` queries with appropriate timeouts:

```typescript
export const DebouncedSearch: Story = {
  parameters: {
    msw: {
      handlers: fsHandlers
    }
  },
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement)
    const input = canvas.getByPlaceholderText(/search/i)

    // Type search query
    await userEvent.type(input, 'test')

    // Wait for debounce (e.g., 250ms) and API response
    // findByRole waits up to 1000ms by default, or use custom timeout
    const modal = await canvas.findByRole('dialog', {}, { timeout: 3000 })
    await expect(modal).toBeInTheDocument()
  }
}
```

### Best Practices

1. **Organize Handlers by Resource**: Follow the file naming convention in `msw/resources/README.md`
2. **Import API_BASE_URL**: Always use `API_BASE_URL` from `@/constants/uri` for consistency
3. **Reuse Type Definitions**: Import response types from corresponding API client files
4. **Test Multiple Scenarios**: Create stories for success, empty, and error states
5. **Use Async Queries**: Use `findBy*` queries when waiting for API responses
6. **Add Timeouts**: Increase timeout for debounced or slow API calls

### Common MSW Patterns

#### Pattern 1: GET Request

```typescript
http.get<never, never, SessionListResponse>(
  `${API_BASE_URL}/sessions`,
  () => {
    return HttpResponse.json({
      sessions: [
        { id: '1', title: 'Session 1' },
        { id: '2', title: 'Session 2' }
      ]
    })
  }
)
```

#### Pattern 2: POST Request with Body

```typescript
http.post<never, CreateSessionRequest, CreateSessionResponse>(
  `${API_BASE_URL}/sessions`,
  async ({ request }) => {
    const body = await request.json()

    return HttpResponse.json({
      id: 'new-session',
      title: body.title
    })
  }
)
```

#### Pattern 3: Error Response

```typescript
http.get(`${API_BASE_URL}/sessions/:id`, () => {
  return HttpResponse.json(
    { message: 'Session not found' },
    { status: 404 }
  )
})
```

#### Pattern 4: Delayed Response (Simulating Network Latency)

```typescript
import { delay, http, HttpResponse } from 'msw'

http.get(`${API_BASE_URL}/sessions`, async () => {
  await delay(1000)  // 1 second delay

  return HttpResponse.json({ sessions: [] })
})
```

### Troubleshooting

#### Issue: "Did you forget to run npx msw init"

**Cause**: Service Worker file is missing or not being served.

**Solution**:
1. Ensure `.storybook/public/mockServiceWorker.js` exists
2. Verify `staticDirs: ['./public']` is in `.storybook/main.ts`
3. Restart Storybook

#### Issue: Mock handlers not working

**Cause**: Handlers not properly registered or incorrect URL.

**Solution**:
1. Verify handler URL matches the API endpoint exactly
2. Check that `msw` parameters are added to the story
3. Ensure MSW is initialized in `.storybook/preview.ts`
4. Check browser console for MSW logs

#### Issue: Tests pass but API calls go to real server

**Cause**: MSW not intercepting requests.

**Solution**:
1. Check that `mswLoader` is in the `loaders` array in `.storybook/preview.ts`
2. Verify `initialize()` is called before the preview config
3. Clear browser cache and restart Storybook

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
