# TypeScript Project Guidelines

## Overview

This document defines project-wide TypeScript conventions, forbidden patterns, and automated validation tools. These rules apply across all layers (hooks, components, stores, API, forms) to maintain code quality and consistency.

## Core Principles

1. **Explicit over implicit** - Always define return types for exported functions
2. **Type safety first** - Avoid `any`, prefer strict typing
3. **Consistent patterns** - Follow established project conventions
4. **Automated enforcement** - Use ESLint and TypeScript compiler to catch violations

## Forbidden Patterns

### ❌ 1. Direct `fetch` Usage in API Functions

**Rule:** Never use `fetch` directly. Always use the centralized `client` from `@/lib/api/client`.

```typescript
// ❌ BAD: Direct fetch usage
export const getSession = async (id: string) => {
  const response = await fetch(`/api/sessions/${id}`)
  return response.json()
}

// ✅ GOOD: Use client
import { client } from '@/lib/api/client'

export const getSession = async (id: string): Promise<SessionDetail> => {
  return client.get<SessionDetail>(`/sessions/${id}`)
}
```

**Reason:** Centralized error handling, consistent request formatting, and type safety.

**Enforcement:** ESLint rule (to be implemented)

```javascript
// eslint.config.js
{
  'no-restricted-globals': ['error', {
    name: 'fetch',
    message: 'Use client from @/lib/api/client instead of fetch directly'
  }]
}
```

### ❌ 2. Exception Handling in API Functions

**Rule:** API functions must NOT handle exceptions. Let errors propagate to Actions hooks.

```typescript
// ❌ BAD: Exception handling in API layer
export const deleteSession = async (id: string): Promise<void> => {
  try {
    await client.delete(`/sessions/${id}`)
  } catch (error) {
    console.error('Failed to delete session:', error)
    throw error
  }
}

// ✅ GOOD: Let errors propagate
export const deleteSession = async (id: string): Promise<void> => {
  await client.delete(`/sessions/${id}`)
}
```

**Reason:** Error handling is the responsibility of Actions hooks, which manage toast notifications via `useAppStore`.

**Enforcement:** Code review + grep check

```bash
# Check for try-catch in API files
grep -r "try {" src/web/lib/api/*.ts
```

### ❌ 3. Zod Schemas Outside `schema.ts` Files

**Rule:** Zod schemas must only be defined in `schema.ts` files (except `@/lib/validation/*`).

```typescript
// ❌ BAD: Schema in component file
// MyForm.tsx
import { z } from 'zod'
const schema = z.object({ name: z.string() })

// ✅ GOOD: Schema in dedicated file
// schema.ts
import { z } from 'zod'
export const myFormSchema = z.object({ name: z.string() })

// MyForm.tsx
import { myFormSchema } from './schema'
```

**Reason:** Separation of concerns, easier testing, and consistent location for validation logic.

**Enforcement:** ESLint rule (already implemented)

```javascript
// eslint.config.js
{
  'no-restricted-imports': ['error', {
    paths: [{
      name: 'zod',
      message: 'Zod imports are only allowed in schema.ts files or @/lib/validation/*'
    }]
  }]
}
```

### ❌ 4. Store Access from Molecules/Atoms

**Rule:** Molecules and Atoms must NOT directly access stores (Context). Only Pages and Organisms can access stores.

```typescript
// ❌ BAD: Molecule accessing store directly
// components/molecules/InputGroup/InputGroup.tsx
import { useAppStore } from '@/stores/useAppStore'

const InputGroup = () => {
  const { pushToast } = useAppStore()  // FORBIDDEN
  // ...
}

// ✅ GOOD: Receive callbacks via props
// components/molecules/InputGroup/InputGroup.tsx
type InputGroupProps = {
  onError?: (message: string) => void
}

const InputGroup = ({ onError }: InputGroupProps) => {
  // Call parent's error handler
  onError?.('Validation failed')
}

// Organism provides the callback
const MyOrganism = () => {
  const { pushToast } = useAppStore()

  return (
    <InputGroup
      onError={(msg) => pushToast({ status: 'error', description: msg })}
    />
  )
}
```

**Reason:** Maintains clear component hierarchy and prevents tight coupling to global state.

**Enforcement:** ESLint rule

```javascript
// eslint.config.js
{
  'no-restricted-imports': ['error', {
    patterns: [{
      group: ['*/stores/*'],
      importNames: ['useAppStore', 'use*Store'],
      // Apply only to molecules/ and atoms/ directories
      message: 'Molecules and Atoms cannot access stores directly. Receive data via props.'
    }]
  }]
}
```

### ❌ 5. Mixing Hook Patterns

**Rule:** Don't mix Actions, Handlers, and Lifecycle logic in a single hook.

```typescript
// ❌ BAD: Mixed responsibilities
const useEverything = () => {
  const [data, setData] = useState<Session[]>([])

  // API call (Actions)
  const fetchSessions = async () => {
    const sessions = await getSessions()
    setData(sessions)
  }

  // Event handler (Handlers)
  const handleDelete = (id: string) => {
    // ...
  }

  // Side effect (Lifecycle)
  useEffect(() => {
    fetchSessions()
  }, [])

  return { data, handleDelete, fetchSessions }
}

// ✅ GOOD: Separated concerns
const useSessionActions = () => {
  const fetchSessions = async (): Promise<Session[]> => {
    return getSessions()
  }
  const deleteSession = async (id: string): Promise<void> => {
    return deleteSession(id)
  }
  return { fetchSessions, deleteSession }
}

const useSessionHandlers = (actions: ReturnType<typeof useSessionActions>) => {
  const { pushToast } = useAppStore()

  const handleDelete = async (id: string): Promise<void> => {
    try {
      await actions.deleteSession(id)
      pushToast({ status: 'success', description: 'Deleted successfully' })
    } catch {
      pushToast({ status: 'error', description: 'Failed to delete' })
    }
  }

  return { handleDelete }
}

const useSessionLifecycle = (actions: ReturnType<typeof useSessionActions>) => {
  const [sessions, setSessions] = useState<Session[]>([])

  useEffect(() => {
    actions.fetchSessions().then(setSessions)
  }, [])

  return { sessions }
}
```

**Reason:** Clear separation of concerns, easier testing, and better reusability.

**Enforcement:** Code review

### ❌ 6. Implicit `any` Types

**Rule:** Never rely on implicit `any`. Always define explicit types.

```typescript
// ❌ BAD: Implicit any
const processData = (data) => {
  // data: any (implicit)
  return data.map((item) => item.value)
}

// ✅ GOOD: Explicit types
const processData = (data: DataItem[]): number[] => {
  return data.map((item) => item.value)
}
```

**Reason:** Type safety and better IDE support.

**Enforcement:** TypeScript compiler flag

```json
// tsconfig.json
{
  "compilerOptions": {
    "noImplicitAny": true,
    "strict": true
  }
}
```

### ❌ 7. Missing Return Types on Exported Functions

**Rule:** All exported functions must have explicit return types.

```typescript
// ❌ BAD: No return type
export const calculateTotal = (items: Item[]) => {
  return items.reduce((sum, item) => sum + item.price, 0)
}

// ✅ GOOD: Explicit return type
export const calculateTotal = (items: Item[]): number => {
  return items.reduce((sum, item) => sum + item.price, 0)
}
```

**Reason:** Better documentation, type safety, and API clarity.

**Enforcement:** ESLint rule (already implemented)

```javascript
// eslint.config.js
{
  '@typescript-eslint/explicit-function-return-type': ['error', {
    allowExpressions: true,
    allowTypedFunctionExpressions: true
  }]
}
```

### ❌ 8. Type Assertions Without Validation

**Rule:** Avoid `as` type assertions without runtime validation.

```typescript
// ❌ BAD: Unsafe type assertion
const data = JSON.parse(response) as SessionDetail

// ✅ GOOD: Use Zod for runtime validation
import { z } from 'zod'
import { sessionDetailSchema } from './schema'

const data = sessionDetailSchema.parse(JSON.parse(response))
```

**Reason:** Type assertions bypass TypeScript's type checking and can lead to runtime errors.

**Enforcement:** Code review + ESLint rule

```javascript
// eslint.config.js
{
  '@typescript-eslint/consistent-type-assertions': ['error', {
    assertionStyle: 'as',
    objectLiteralTypeAssertions: 'never'
  }]
}
```

## Recommended Patterns

### ✅ 1. Use Validation Rules from `@/lib/validation`

Always prefer reusable validation rules over inline Zod schemas.

```typescript
// ✅ GOOD: Reusable rules
import { object } from 'zod'
import { requiredString, emailString, optionalNumber } from '@/lib/validation'

export const userSchema = object({
  name: requiredString('Name'),
  email: emailString('Email'),
  age: optionalNumber(0, 120)
})
```

### ✅ 2. Chain Zod Methods for Custom Validation

Validation rules return Zod schemas, so you can chain additional methods.

```typescript
// ✅ GOOD: Chaining methods
import { requiredString } from '@/lib/validation'

export const schema = object({
  username: requiredString('Username', 3)
    .max(20)
    .regex(/^[a-zA-Z0-9_]+$/),
  bio: requiredString('Bio').max(500)
})
```

### ✅ 3. Use Barrel Exports

Export multiple related items from an `index.ts` file.

```typescript
// ✅ GOOD: Barrel export
// lib/validation/index.ts
export * from './stringRules'
export * from './numberRules'
export * from './enumRules'

// Usage
import { requiredString, optionalNumber, enumFromList } from '@/lib/validation'
```

### ✅ 4. Define Custom Types in Dedicated Files

Create `types.ts` files for shared type definitions.

```typescript
// ✅ GOOD: Dedicated types file
// types/session.ts
export type Session = {
  id: string
  purpose: string
  created_at: string
}

export type SessionDetail = Session & {
  background: string
  roles: string[]
  turns: Turn[]
}
```

## Automated Validation Tools

### 1. ESLint

Run ESLint to catch forbidden patterns:

```bash
# Check all TypeScript files
npm run lint

# Auto-fix where possible
npm run lint:fix
```

### 2. TypeScript Compiler (ts_checker)

**Critical:** Always run TypeScript type checking before committing code.

Use strict TypeScript settings:

```json
// tsconfig.json
{
  "compilerOptions": {
    "strict": true,
    "noImplicitAny": true,
    "strictNullChecks": true,
    "strictFunctionTypes": true,
    "noUnusedLocals": true,
    "noUnusedParameters": true,
    "noImplicitReturns": true
  }
}
```

Run type checking:

```bash
# Check all files for type errors
npm run type-check
# or
npx tsc --noEmit

# Check specific file
npx tsc --noEmit path/to/file.ts
```

**Best Practice:** Run `ts_checker` (TypeScript compiler) after every significant change to catch type errors early. This is especially important for:

- Adding new functions or types
- Modifying existing APIs
- Refactoring component props
- Changing store or hook signatures

### 3. Pre-commit Hooks

Validate code before commits:

```bash
# Install husky
npm install --save-dev husky

# Add pre-commit hook
npx husky add .husky/pre-commit "npm run lint && npm run type-check"
```

### 4. CI/CD Pipeline

Add validation to GitHub Actions:

```yaml
# .github/workflows/lint.yml
name: Lint and Type Check

on: [push, pull_request]

jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
        with:
          node-version: '18'
      - run: npm ci
      - run: npm run lint
      - run: npm run type-check
      - name: Check for fetch usage in API files
        run: |
          if grep -r "fetch(" src/web/lib/api/*.ts; then
            echo "Error: Direct fetch usage found in API files"
            exit 1
          fi
```

### 5. Custom Grep Checks

Add custom validation scripts:

```bash
#!/bin/bash
# scripts/validate-patterns.sh

echo "Checking for forbidden patterns..."

# Check 1: fetch usage in API files
if grep -r "fetch(" src/web/lib/api/*.ts; then
  echo "❌ Error: Direct fetch usage found in API files"
  exit 1
fi

# Check 2: try-catch in API files
if grep -r "try {" src/web/lib/api/*.ts; then
  echo "❌ Error: Exception handling found in API files"
  exit 1
fi

# Check 3: Zod imports outside schema.ts
if find src/web/components -name "*.tsx" -o -name "*.ts" | \
   grep -v "schema.ts" | \
   xargs grep "from 'zod'"; then
  echo "❌ Error: Zod import found outside schema.ts"
  exit 1
fi

echo "✅ All pattern checks passed"
```

Make it executable and run:

```bash
chmod +x scripts/validate-patterns.sh
./scripts/validate-patterns.sh
```

### 6. Advanced TypeScript Tools (Available in Some Environments)

Some development environments provide additional TypeScript analysis tools that can significantly improve code quality and development speed. While these tools may not be available in all IDEs, they offer powerful capabilities for TypeScript projects:

#### ts_find_similar_code

Finds code patterns similar to a given snippet across the codebase.

**Use Cases:**

- Identify duplicate logic that could be refactored into shared utilities
- Find existing implementations before writing new code
- Discover inconsistent patterns that should be standardized

**Example:**

```typescript
// Find similar API call patterns
// Input: client.get<Session>('/sessions')
// Output: All similar client.get calls with Session type across the codebase
```

**Benefits:**

- Reduces code duplication
- Promotes code reuse
- Ensures consistency across the project

#### ts_get_code_snippet

Extracts a specific function or type definition from the codebase.

**Use Cases:**

- Quickly retrieve implementation details of a specific function
- Get type definitions for API integration
- Reference existing patterns when implementing similar features

**Example:**

```typescript
// Get the implementation of requiredString function
// Returns: Complete function definition with types and JSDoc
export const requiredString = (
  fieldName: string,
  minLength: number = 1
): z.ZodString => { ... }
```

**Benefits:**

- Faster code navigation
- Better understanding of existing implementations
- Reduces context switching

#### ts_get_references

Finds all usages of a function, type, or variable across the codebase.

**Use Cases:**

- Understand impact before refactoring
- Find usage examples of a utility function
- Identify dead code (no references)
- Track down all callers of an API function

**Example:**

```typescript
// Find all usages of useAppStore
// Returns:
// - components/organisms/SessionList/SessionList.tsx:15
// - components/organisms/StartSessionForm/StartSessionForm.tsx:23
// - components/pages/SessionListPage.tsx:18
```

**Benefits:**

- Safe refactoring (know all affected files)
- Better code comprehension
- Easier impact analysis

#### ts_get_type_definitions

Retrieves type definitions for a symbol, including inferred types.

**Use Cases:**

- Understand complex inferred types
- Verify API response types
- Debug type mismatches
- Document component prop types

**Example:**

```typescript
// Get type definition of client.get response
// Input: const sessions = await client.get<Session[]>('/sessions')
// Output:
// type: Promise<Session[]>
// Session: {
//   id: string
//   purpose: string
//   created_at: string
// }
```

**Benefits:**

- Better type understanding
- Faster debugging of type issues
- Improved documentation

#### Integration Workflow

When these tools are available, use them in your workflow:

1. **Before implementing** - Use `ts_find_similar_code` to check for existing patterns
2. **During development** - Use `ts_get_code_snippet` to reference existing implementations
3. **Before refactoring** - Use `ts_get_references` to understand impact
4. **When debugging types** - Use `ts_get_type_definitions` to verify types

**Note:** These tools are provided by advanced TypeScript language servers and may not be available in all development environments. Check your tooling documentation for availability.

## Integration with Other Roles

This document provides **project-wide TypeScript conventions**. For domain-specific guidelines, refer to:

- **API patterns** → `api.md`
- **Hook patterns** → `hooks/hooks.md`, `hooks/useActions.md`, etc.
- **Component architecture** → `components/components.md`, `components/organisms.md`, etc.
- **State management** → `stores.md`
- **Form validation** → `rhf.md`

## Enforcement Priority

### High Priority (Must enforce immediately)

1. ✅ Explicit return types on exported functions (ESLint)
2. ✅ Zod schemas only in schema.ts (ESLint)
3. ✅ TypeScript strict mode (tsconfig.json)
4. ⚠️ Direct fetch usage (Add ESLint rule)
5. ⚠️ Store access from Molecules/Atoms (Add ESLint rule)

### Medium Priority (Enforce in code review)

1. No exception handling in API functions
2. Separated hook patterns (Actions/Handlers/Lifecycle)
3. Runtime validation for type assertions
4. Custom grep checks in CI/CD

### Low Priority (Best practices)

1. Barrel exports for related modules
2. Dedicated types files
3. Validation rule reusability

## Summary

By following these conventions and using automated tools, we ensure:

- **Type safety** - Catch errors at compile time
- **Consistency** - Predictable code patterns across the project
- **Maintainability** - Clear separation of concerns
- **Quality** - Automated validation in development and CI/CD

Remember: **These rules exist to help you, not hinder you.** If a rule feels unnecessarily restrictive for a specific case, discuss it with the team before bypassing it.
