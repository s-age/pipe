# React Hook Form (RHF) Usage Guide

## Overview

This project uses React Hook Form (RHF) for form management with Zod for schema validation. We have established reusable validation rules to maintain consistency and reduce code duplication.

## Form Component Pattern

### Basic Structure

```tsx
import { Form } from '@/components/ui/form'
import { formSchema } from './schema'

const MyForm = () => {
  return (
    <Form schema={formSchema}>
      {({ control }) => (
        <FormField
          control={control}
          name="fieldName"
          render={({ field }) => (
            <FormControl>
              <Input {...field} />
            </FormControl>
          )}
        />
      )}
    </Form>
  )
}
```

### Form Component Props

- `schema`: Zod schema object defining validation rules
- Children: Render prop function receiving RHF form methods
- The Form component handles:
  - Form state initialization
  - Validation with zodResolver
  - Error message display
  - Form submission

## Schema Definition (`schema.ts`)

### ESLint Constraint

**CRITICAL**: Zod schemas must only be defined in `schema.ts` files. This is enforced by our ESLint configuration to maintain consistency.

```
✅ MyForm/schema.ts       → Allowed
❌ MyForm/MyForm.tsx      → Not allowed
❌ utils/validation.ts    → Not allowed (except lib/validation/)
```

### File Structure

```typescript
import { object, type TypeOf } from 'zod'
import { requiredString, optionalNumber } from '@/lib/validation'

// 1. Define the schema
export const myFormSchema = object({
  title: requiredString('Title'),
  count: optionalNumber(0, 100)
})

// 2. Export the TypeScript type (optional but recommended)
export type MyFormData = TypeOf<typeof myFormSchema>
```

## Reusable Validation Rules

### Import from Central Library

All validation rules are exported from `@/lib/validation`:

```typescript
import {
  // String rules
  requiredString,
  optionalString,
  commaSeparatedList,
  emailString,
  urlString,
  boundedString,
  patternString,

  // Number rules
  rangedNumber,
  optionalNumber,
  positiveInteger,
  nonNegativeInteger,
  percentage,

  // Enum rules
  enumFromList,
  filePathEnum,
  commaSeparatedFilePathEnum,
  getFilePathOptions
} from '@/lib/validation'
```

### String Validation Examples

```typescript
import { object } from 'zod'
import {
  requiredString,
  optionalString,
  commaSeparatedList,
  emailString,
  urlString,
  boundedString,
  patternString
} from '@/lib/validation'

export const schema = object({
  // Required field with min length
  name: requiredString('Name', 3),

  // Optional field (transforms "" → null)
  description: optionalString(),

  // Comma-separated values → array
  tags: commaSeparatedList(),

  // Email validation
  email: emailString('Email'),

  // URL validation
  website: urlString('Website'),

  // Length constraints (min: 10, max: 100)
  bio: boundedString('Bio', 10, 100),

  // Custom regex pattern
  username: patternString(
    /^[a-zA-Z0-9_]+$/,
    'Username must contain only letters, numbers, and underscores'
  )
})
```

### Number Validation Examples

```typescript
import { object } from 'zod'
import {
  rangedNumber,
  optionalNumber,
  positiveInteger,
  nonNegativeInteger,
  percentage
} from '@/lib/validation'

export const schema = object({
  // Number within range (required)
  age: rangedNumber('Age', 0, 120),

  // Optional number with range
  salary: optionalNumber(0, 1000000),

  // Positive integer (> 0)
  quantity: positiveInteger('Quantity'),

  // Non-negative integer (≥ 0)
  stockCount: nonNegativeInteger('Stock Count'),

  // Percentage (0-100)
  completion: percentage('Completion Rate')
})
```

### Enum Validation Examples

```typescript
import { object } from 'zod'
import {
  enumFromList,
  filePathEnum,
  commaSeparatedFilePathEnum
} from '@/lib/validation'

export const schema = object({
  // Enum from static list
  status: enumFromList(['draft', 'published', 'archived'] as const, 'Status'),

  // Validate file exists in roles/ directory
  role: filePathEnum('roles', 'Role', '.md'),

  // Validate comma-separated file paths
  roles: commaSeparatedFilePathEnum('roles', 'Roles', '.md')
})
```

### Getting File Options for UI Dropdowns

Use `getFilePathOptions()` helper to populate dropdown menus:

```typescript
import { getFilePathOptions } from '@/lib/validation'

// In your component
const roleOptions = getFilePathOptions('roles', '.md', false)
// Returns: ['roles/developer.md', 'roles/designer.md', ...]

// Use in Select component
<Select>
  {roleOptions.map((path) => (
    <SelectItem key={path} value={path}>
      {path.replace('roles/', '').replace('.md', '')}
    </SelectItem>
  ))}
</Select>
```

## Real-World Example: StartSessionForm

### Before Refactoring

```typescript
// ❌ Duplicated logic, hard to maintain
export const formSchema = object({
  purpose: string().min(1, 'Purpose is required'),
  roles: string()
    .transform((value) =>
      value
        ? value
            .split(',')
            .map((s) => s.trim())
            .filter(Boolean)
        : null
    )
    .nullable()
    .default(null),
  parent: string()
    .transform((value) => (value === '' ? null : value))
    .nullable()
    .default(null),
  references: string()
    .transform((value) =>
      value
        ? value
            .split(',')
            .map((s) => s.trim())
            .filter(Boolean)
            .map((path) => ({ path }))
        : null
    )
    .nullable()
    .default(null)
})
```

### After Refactoring

```typescript
// ✅ Clean, reusable, maintainable
import { object } from 'zod'
import {
  requiredString,
  optionalString,
  commaSeparatedList,
  optionalNumber
} from '@/lib/validation'

export const formSchema = object({
  purpose: requiredString('Purpose'),
  roles: commaSeparatedList(),
  parent: optionalString(),
  references: commaSeparatedList().transform((paths) =>
    paths ? paths.map((path) => ({ path })) : null
  ),
  hyperparameters: object({
    temperature: optionalNumber(0, 2).default(0.7),
    top_p: optionalNumber(0, 1).default(0.9)
  })
    .nullable()
    .default(null)
})
```

## Custom Transformations

You can chain custom transformations on top of validation rules:

```typescript
import { commaSeparatedList } from '@/lib/validation'

export const schema = object({
  // Transform comma-separated paths to reference objects
  references: commaSeparatedList().transform((paths) =>
    paths ? paths.map((path) => ({ path, type: 'file' })) : null
  ),

  // Normalize and uppercase tags
  tags: commaSeparatedList().transform((tags) =>
    tags ? tags.map((tag) => tag.toUpperCase()) : null
  )
})
```

## Error Handling

### Default Error Messages

Validation rules provide default error messages:

```typescript
requiredString('Name') // "Name is required"
rangedNumber('Age', 0, 120) // "Age must be between 0 and 120"
emailString('Email') // "Please enter a valid email address"
```

### Custom Error Messages

Override error messages when needed:

```typescript
import { string } from 'zod'

export const schema = object({
  // Override with custom message
  email: string()
    .email('Please provide a valid business email address')
    .refine(
      (email) => email.endsWith('@company.com'),
      'Only company email addresses are allowed'
    )
})
```

### Field-Level Error Display

The Form component automatically displays errors:

```tsx
<FormField
  control={control}
  name="email"
  render={({ field, fieldState }) => (
    <FormItem>
      <FormLabel>Email</FormLabel>
      <FormControl>
        <Input {...field} />
      </FormControl>
      {/* Error automatically shown by FormMessage */}
      <FormMessage />
    </FormItem>
  )}
/>
```

## Best Practices

### 1. Use Reusable Rules First

```typescript
// ✅ Good: Use existing rules
import { requiredString } from '@/lib/validation'
const schema = object({ name: requiredString('Name') })

// ❌ Avoid: Reinventing the wheel
import { string } from 'zod'
const schema = object({ name: string().min(1, 'Name is required') })
```

### 2. Create New Rules for Common Patterns

If you find yourself copying the same validation logic 3+ times, create a new rule in `src/web/lib/validation/`:

```typescript
// src/web/lib/validation/customRules.ts
import { z } from 'zod'

export const phoneNumber = (fieldName: string): z.ZodString => {
  return z
    .string()
    .regex(/^\+?[1-9]\d{1,14}$/, `${fieldName} must be a valid phone number`)
}

// Export from index.ts
export { phoneNumber } from './customRules'
```

### 3. Keep schema.ts Files Simple

```typescript
// ✅ Good: Clean and declarative
export const schema = object({
  name: requiredString('Name'),
  email: emailString('Email'),
  age: rangedNumber('Age', 18, 100)
})

// ❌ Avoid: Complex logic in schema files
export const schema = object({
  name: string().transform((val) => {
    // 20 lines of transformation logic...
  })
})
```

### 4. Type Safety

Always export TypeScript types from schemas:

```typescript
import { type TypeOf } from 'zod'

export const mySchema = object({
  name: requiredString('Name')
})

// Export for use in components
export type MyFormData = TypeOf<typeof mySchema>
```

## Integration with Forms

### Complete Form Example

```tsx
import { Button } from '@/components/ui/button'
import {
  Form,
  FormControl,
  FormField,
  FormItem,
  FormLabel,
  FormMessage
} from '@/components/ui/form'
import { Input } from '@/components/ui/input'
import { formSchema } from './schema'

export const UserForm = () => {
  const handleSubmit = (data: TypeOf<typeof formSchema>) => {
    console.log('Form data:', data)
    // Handle form submission
  }

  return (
    <Form schema={formSchema} onSubmit={handleSubmit}>
      {({ control }) => (
        <>
          <FormField
            control={control}
            name="name"
            render={({ field }) => (
              <FormItem>
                <FormLabel>Name</FormLabel>
                <FormControl>
                  <Input {...field} placeholder="Enter your name" />
                </FormControl>
                <FormMessage />
              </FormItem>
            )}
          />

          <FormField
            control={control}
            name="email"
            render={({ field }) => (
              <FormItem>
                <FormLabel>Email</FormLabel>
                <FormControl>
                  <Input {...field} type="email" placeholder="your@email.com" />
                </FormControl>
                <FormMessage />
              </FormItem>
            )}
          />

          <Button type="submit">Submit</Button>
        </>
      )}
    </Form>
  )
}
```

## Common Patterns

### Optional Fields with Defaults

```typescript
import { object } from 'zod'
import { optionalString, optionalNumber } from '@/lib/validation'

export const schema = object({
  // Optional with null default
  description: optionalString(),

  // Optional with custom default
  priority: optionalNumber().default(5),

  // Optional with nested defaults
  settings: object({
    theme: optionalString().default('light'),
    fontSize: optionalNumber(10, 24).default(14)
  })
    .nullable()
    .default(null)
})
```

### Conditional Validation

```typescript
import { object, boolean } from 'zod'
import { requiredString, optionalString } from '@/lib/validation'

export const schema = object({
  hasAddress: boolean().default(false),
  address: optionalString()
}).refine((data) => !data.hasAddress || (data.hasAddress && data.address), {
  message: 'Address is required when "Has Address" is checked',
  path: ['address']
})
```

### Array Validation

```typescript
import { object, array } from 'zod'
import { requiredString, emailString } from '@/lib/validation'

export const schema = object({
  members: array(
    object({
      name: requiredString('Member Name'),
      email: emailString('Member Email')
    })
  ).min(1, 'At least one member is required')
})
```

## Migration Guide

When migrating existing schemas to use validation rules:

1. **Identify duplicate patterns** in your current schema
2. **Replace with validation rules** from `@/lib/validation`
3. **Test thoroughly** - validation behavior should remain identical
4. **Remove old imports** - keep only necessary Zod imports

Example migration:

```typescript
// Before
import { object, string, coerce } from 'zod'

export const schema = object({
  title: string().min(1, 'Title is required'),
  count: coerce.number().min(0).max(100).nullable().default(null)
})

// After
import { object } from 'zod'
import { requiredString, optionalNumber } from '@/lib/validation'

export const schema = object({
  title: requiredString('Title'),
  count: optionalNumber(0, 100)
})
```

## Additional Resources

- See existing `schema.ts` files for more examples:
  - `StartSessionForm/schema.ts` - Complex form with nested objects
  - `ChatHistory/schema.ts` - Simple single-field form
- Refer to `src/web/lib/validation/` for validation rule implementations
- React Hook Form docs: https://react-hook-form.com/
- Zod docs: https://zod.dev/
