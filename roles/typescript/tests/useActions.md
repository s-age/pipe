# Role: Custom Hook Unit Testing (TypeScript)

## Overview

This role defines **HOW** to write unit tests for custom React hooks, particularly hooks that handle user actions (e.g., `useActions` pattern). It covers testing hooks that call APIs, manage side effects, and display toast notifications.

## Core Principles

1. **Isolation** - Test hooks in isolation using `@testing-library/react`'s `renderHook`
2. **Mock API Calls** - Use MSW (Mock Service Worker) to mock HTTP requests
3. **Test Side Effects** - Verify toast notifications and async state changes
4. **Type Safety** - Use TypeScript types from the hook and API client files
5. **Comprehensive Coverage** - Test success cases, error cases, and edge cases

## Test File Structure

### Location Pattern

Unit tests for hooks are placed in a `__tests__` directory next to the hook file:

```
hooks/
├── useTurnActions.ts
└── __tests__/
    └── useTurnActions.test.ts
```

### Basic Test Template

```typescript
import { renderHook, waitFor } from '@testing-library/react'
import { setupServer } from 'msw/node'

import type { Turn } from '@/lib/api/session/getSession'
import { turnHandlers, turnErrorHandlers } from '@/msw/resources/turn'
import { clearToasts, getToasts } from '@/stores/useToastStore'

import { useTurnActions } from '../useTurnActions'

const server = setupServer(...turnHandlers)

describe('useTurnActions', () => {
  beforeAll(() => server.listen())
  afterEach(() => {
    server.resetHandlers()
    clearToasts()
  })
  afterAll(() => server.close())

  describe('deleteTurnAction', () => {
    it('should delete turn successfully and show success toast', async () => {
      const { result } = renderHook(() => useTurnActions())

      await result.current.deleteTurnAction('test-session-id', 1)

      await waitFor(() => {
        const toasts = getToasts()
        expect(toasts).toHaveLength(1)
        expect(toasts[0].status).toBe('success')
        expect(toasts[0].title).toBe('Turn deleted successfully')
      })
    })
  })
})
```

## Setting Up MSW for Unit Tests

### Step 1: Check for Existing MSW Handlers

Before creating new MSW handlers, check if handlers already exist for the API endpoints you need to test:

```bash
# Check src/web/msw/resources/ directory
ls src/web/msw/resources/
```

Look for a file matching the first path segment after `/api/v1/`:

| Endpoint | Expected File |
|----------|---------------|
| `/api/v1/turn/delete` | `turn.ts` |
| `/api/v1/session/create` | `session.ts` |
| `/api/v1/user/profile` | `user.ts` |

### Step 2: Create MSW Handlers (If Needed)

If handlers don't exist, create them following the [MSW Resources README](../../../src/web/msw/resources/README.md):

**File**: `src/web/msw/resources/turn.ts`

```typescript
import { http, HttpResponse } from 'msw'

import { API_BASE_URL } from '@/constants/uri'

/**
 * MSW handlers for /turn endpoints
 */
export const turnHandlers = [
  // DELETE /api/v1/session/:sessionId/turn/:turnIndex
  http.delete<{ sessionId: string; turnIndex: string }, never, { message: string }>(
    `${API_BASE_URL}/session/:sessionId/turn/:turnIndex`,
    () => {
      return HttpResponse.json({
        message: 'Turn deleted successfully'
      })
    }
  ),

  // PATCH /api/v1/session/:sessionId/turn/:turnIndex
  http.patch<
    { sessionId: string; turnIndex: string },
    Record<string, unknown>,
    { message: string }
  >(`${API_BASE_URL}/session/:sessionId/turn/:turnIndex`, async ({ request }) => {
    await request.json()

    return HttpResponse.json({
      message: 'Turn updated successfully'
    })
  }),

  // POST /api/v1/session/:sessionId/fork/:forkIndex
  http.post<
    { sessionId: string; forkIndex: string },
    never,
    { newSessionId: string }
  >(
    `${API_BASE_URL}/session/:sessionId/fork/:forkIndex`,
    ({ params }) => {
      return HttpResponse.json({
        newSessionId: `forked-session-${params.sessionId}`
      })
    }
  )
]

/**
 * MSW handlers for /turn endpoints with error responses
 */
export const turnErrorHandlers = [
  // DELETE /api/v1/session/:sessionId/turn/:turnIndex (error response)
  http.delete(
    `${API_BASE_URL}/session/:sessionId/turn/:turnIndex`,
    () =>
      new HttpResponse(JSON.stringify({ message: 'Failed to delete turn' }), {
        status: 500,
        headers: { 'Content-Type': 'application/json' }
      })
  ),

  // PATCH /api/v1/session/:sessionId/turn/:turnIndex (error response)
  http.patch(
    `${API_BASE_URL}/session/:sessionId/turn/:turnIndex`,
    () =>
      new HttpResponse(JSON.stringify({ message: 'Failed to update turn' }), {
        status: 500,
        headers: { 'Content-Type': 'application/json' }
      })
  ),

  // POST /api/v1/session/:sessionId/fork/:forkIndex (error response)
  http.post(
    `${API_BASE_URL}/session/:sessionId/fork/:forkIndex`,
    () =>
      new HttpResponse(JSON.stringify({ message: 'Failed to fork session' }), {
        status: 500,
        headers: { 'Content-Type': 'application/json' }
      })
  )
]
```

**Key principles for MSW handlers**:
- Always import `API_BASE_URL` from `@/constants/uri`
- Reuse type definitions from corresponding API client files
- Export separate handler arrays for success and error scenarios
- Use proper TypeScript generics: `http.method<PathParams, RequestBody, ResponseBody>`

### Step 3: Set Up Test Environment

Configure Vitest for unit tests in `vite.config.ts`:

```typescript
/// <reference types="vitest/config" />
import { fileURLToPath } from 'node:url'
import path from 'path'

import { vanillaExtractPlugin } from '@vanilla-extract/vite-plugin'
import react from '@vitejs/plugin-react'
import { defineConfig } from 'vite'

const dirname =
  typeof __dirname !== 'undefined'
    ? __dirname
    : path.dirname(fileURLToPath(import.meta.url))

export default defineConfig({
  plugins: [react(), vanillaExtractPlugin()],
  resolve: {
    alias: {
      '@': path.resolve(dirname, '.')
    }
  },
  test: {
    globals: true,
    environment: 'jsdom',
    setupFiles: ['./vitest.setup.ts'],
    include: ['**/__tests__/**/*.test.{ts,tsx}']
  }
})
```

**Critical configuration points**:
1. **Path alias**: Use `dirname` variable (not `__dirname`) for ES module compatibility
2. **Environment**: Set to `jsdom` for DOM-based hook testing
3. **Setup file**: Create `vitest.setup.ts` for test utilities

**File**: `vitest.setup.ts`

```typescript
import '@testing-library/jest-dom/vitest'
```

### Step 4: Update package.json

Add test script:

```json
{
  "scripts": {
    "test": "vitest"
  },
  "devDependencies": {
    "jsdom": "^27.4.0"
  }
}
```

**Note**: Install `jsdom` if not already present: `npm install --save-dev jsdom`

## Test Patterns

### Pattern 1: Testing Successful API Calls

Test that the hook calls the API correctly and displays a success toast:

```typescript
describe('deleteTurnAction', () => {
  it('should delete turn successfully and show success toast', async () => {
    const { result } = renderHook(() => useTurnActions())

    await result.current.deleteTurnAction('test-session-id', 1)

    await waitFor(() => {
      const toasts = getToasts()
      expect(toasts).toHaveLength(1)
      expect(toasts[0].status).toBe('success')
      expect(toasts[0].title).toBe('Turn deleted successfully')
    })
  })
})
```

**Key points**:
- Use `renderHook()` to render the hook
- Access hook return value via `result.current`
- Use `waitFor()` for async assertions
- Verify toast notifications using store getters

### Pattern 2: Testing Error Handling

Test that the hook handles API errors and displays error toasts:

```typescript
describe('deleteTurnAction', () => {
  it('should handle delete turn error and show failure toast', async () => {
    server.use(...turnErrorHandlers)
    const { result } = renderHook(() => useTurnActions())

    await result.current.deleteTurnAction('test-session-id', 1)

    await waitFor(() => {
      const toasts = getToasts()
      expect(toasts).toHaveLength(1)
      expect(toasts[0].status).toBe('failure')
      expect(toasts[0].title).toBe('Failed to delete turn')
    })
  })
})
```

**Key points**:
- Use `server.use()` to override handlers with error versions
- Test is structured identically to success case
- Verify error toast content

### Pattern 3: Testing Return Values

Test that the hook returns expected values from API calls:

```typescript
describe('forkSessionAction', () => {
  it('should fork session successfully and return new session ID', async () => {
    const { result } = renderHook(() => useTurnActions())

    const newSessionId = await result.current.forkSessionAction('test-session-id', 2)

    await waitFor(() => {
      const toasts = getToasts()
      expect(toasts).toHaveLength(1)
      expect(toasts[0].status).toBe('success')
      expect(toasts[0].title).toBe('Session forked successfully')
    })
    expect(newSessionId).toBe('forked-session-test-session-id')
  })

  it('should handle fork session error and return undefined', async () => {
    server.use(...turnErrorHandlers)
    const { result } = renderHook(() => useTurnActions())

    const newSessionId = await result.current.forkSessionAction('test-session-id', 2)

    await waitFor(() => {
      const toasts = getToasts()
      expect(toasts).toHaveLength(1)
      expect(toasts[0].status).toBe('failure')
      expect(toasts[0].title).toBe('Failed to fork session')
    })
    expect(newSessionId).toBeUndefined()
  })
})
```

**Key points**:
- Test both success and error return values
- Verify toast notifications in both cases
- Use appropriate matchers (`toBe`, `toBeUndefined`)

### Pattern 4: Testing Conditional Logic

Test hooks with conditional behavior based on input:

```typescript
describe('editTurnAction', () => {
  it('should edit user_task turn successfully with instruction field', async () => {
    const { result } = renderHook(() => useTurnActions())
    const userTaskTurn: Turn = {
      type: 'user_task',
      instruction: 'original instruction',
      timestamp: '2024-01-01T00:00:00Z'
    }

    await result.current.editTurnAction(
      'test-session-id',
      0,
      'updated instruction',
      userTaskTurn
    )

    await waitFor(() => {
      const toasts = getToasts()
      expect(toasts).toHaveLength(1)
      expect(toasts[0].status).toBe('success')
      expect(toasts[0].title).toBe('Turn updated successfully')
    })
  })

  it('should edit model_response turn successfully with content field', async () => {
    const { result } = renderHook(() => useTurnActions())
    const modelResponseTurn: Turn = {
      type: 'model_response',
      content: 'original content',
      timestamp: '2024-01-01T00:00:00Z'
    }

    await result.current.editTurnAction(
      'test-session-id',
      1,
      'updated content',
      modelResponseTurn
    )

    await waitFor(() => {
      const toasts = getToasts()
      expect(toasts).toHaveLength(1)
      expect(toasts[0].status).toBe('success')
      expect(toasts[0].title).toBe('Turn updated successfully')
    })
  })
})
```

**Key points**:
- Create type-safe test data using imported types
- Test all conditional branches
- Verify behavior is correct for each input variation

### Pattern 5: Testing Hook Structure

Test that the hook exports the expected interface:

```typescript
describe('return value structure', () => {
  it('should return all three action functions', () => {
    const { result } = renderHook(() => useTurnActions())

    expect(result.current).toHaveProperty('deleteTurnAction')
    expect(result.current).toHaveProperty('editTurnAction')
    expect(result.current).toHaveProperty('forkSessionAction')
    expect(typeof result.current.deleteTurnAction).toBe('function')
    expect(typeof result.current.editTurnAction).toBe('function')
    expect(typeof result.current.forkSessionAction).toBe('function')
  })
})
```

**Key points**:
- Verify all expected properties exist
- Verify properties are functions
- Use `toHaveProperty` for clear error messages

## MSW Server Setup

### Basic Server Configuration

```typescript
import { setupServer } from 'msw/node'
import { turnHandlers } from '@/msw/resources/turn'

const server = setupServer(...turnHandlers)

describe('useTurnActions', () => {
  beforeAll(() => server.listen())
  afterEach(() => {
    server.resetHandlers()
    clearToasts()
  })
  afterAll(() => server.close())
})
```

**Lifecycle methods**:
- `beforeAll`: Start MSW server before any tests run
- `afterEach`: Reset handlers to defaults and clean up state (toasts, etc.)
- `afterAll`: Stop MSW server after all tests complete

### Overriding Handlers for Specific Tests

```typescript
it('should handle error', async () => {
  // Override default handlers with error versions
  server.use(...turnErrorHandlers)

  // Test continues...
})
```

**Key points**:
- Use `server.use()` to temporarily override handlers
- Handlers are reset in `afterEach` hook
- No cleanup needed in individual tests

## Testing Toast Notifications

### Accessing Toast State

Import toast store utilities:

```typescript
import { clearToasts, getToasts } from '@/stores/useToastStore'
```

### Verifying Toast Content

```typescript
await waitFor(() => {
  const toasts = getToasts()
  expect(toasts).toHaveLength(1)
  expect(toasts[0].status).toBe('success')
  expect(toasts[0].title).toBe('Turn deleted successfully')
})
```

**Common toast properties**:
- `status`: `'success' | 'failure' | 'warning'`
- `title`: Toast message
- `description`: Optional detailed message
- `duration`: Auto-dismiss timeout
- `dismissible`: Whether user can dismiss

### Cleaning Up Toasts

Always clear toasts between tests:

```typescript
afterEach(() => {
  clearToasts()
})
```

## Common Patterns

### Testing Async Hook Actions

```typescript
it('should perform async action', async () => {
  const { result } = renderHook(() => useMyActions())

  // Call async action
  await result.current.myAction('param')

  // Wait for side effects
  await waitFor(() => {
    expect(getToasts()).toHaveLength(1)
  })
})
```

### Testing Multiple Actions

```typescript
it('should handle multiple sequential actions', async () => {
  const { result } = renderHook(() => useMyActions())

  await result.current.action1()
  await result.current.action2()

  await waitFor(() => {
    const toasts = getToasts()
    expect(toasts).toHaveLength(2)
  })
})
```

### Testing with Different Data Types

```typescript
it.each([
  { type: 'user_task', field: 'instruction' },
  { type: 'model_response', field: 'content' },
  { type: 'function_calling', field: 'response' }
])('should handle $type turn type', async ({ type, field }) => {
  const { result } = renderHook(() => useTurnActions())
  const turn: Turn = {
    type,
    [field]: 'original',
    timestamp: '2024-01-01T00:00:00Z'
  }

  await result.current.editTurnAction('session-id', 0, 'updated', turn)

  await waitFor(() => {
    expect(getToasts()[0].status).toBe('success')
  })
})
```

## Best Practices

1. **Import Types**: Always import types from API client files for type safety
2. **Clean Up State**: Clear toasts and reset MSW handlers in `afterEach`
3. **Use waitFor**: Always use `waitFor` for async assertions
4. **Test Error Cases**: Test both success and error scenarios
5. **Verify Side Effects**: Test toast notifications, not just return values
6. **Descriptive Test Names**: Use clear `it` descriptions that explain what's being tested
7. **Group Related Tests**: Use `describe` blocks to organize tests by action
8. **Reuse MSW Handlers**: Import handlers from `@/msw/resources/`, never define inline

## Running Tests

### Run all unit tests:

```bash
npm test
```

### Run specific test file:

```bash
npm test -- useTurnActions
```

### Run tests in watch mode:

```bash
npm test -- --watch
```

### Run tests in Docker:

```bash
docker compose exec react npm test -- useTurnActions --run
```

## Troubleshooting

### Issue 1: Path Alias Not Working

**Problem**: Tests fail with "Cannot find module '@/msw/resources/turn'"

**Cause**: In ES module environment, `__dirname` is undefined and path alias doesn't resolve correctly.

**Solution**: Use `dirname` variable with `import.meta.url` fallback:

```typescript
const dirname =
  typeof __dirname !== 'undefined'
    ? __dirname
    : path.dirname(fileURLToPath(import.meta.url))

export default defineConfig({
  resolve: {
    alias: {
      '@': path.resolve(dirname, '.')  // Use dirname, not __dirname
    }
  }
})
```

### Issue 2: jsdom Not Found

**Problem**: Tests fail with "Cannot find package 'jsdom'"

**Cause**: `jsdom` package not installed.

**Solution**: Install jsdom:

```bash
npm install --save-dev jsdom
# Or in Docker:
docker compose exec react npm install --save-dev jsdom
```

### Issue 3: Multiple Config Files

**Problem**: Tests fail with "No projects matched the filter 'unit'"

**Cause**: Both `vite.config.ts` and `vitest.config.ts` exist, and Vitest uses the wrong one.

**Solution**: Remove `vitest.config.ts` and configure tests in `vite.config.ts` only:

```bash
rm vitest.config.ts
```

### Issue 4: Toasts Not Clearing Between Tests

**Problem**: Toast count is incorrect because previous test toasts remain.

**Cause**: Missing `clearToasts()` in `afterEach`.

**Solution**: Always clear toasts in `afterEach`:

```typescript
afterEach(() => {
  server.resetHandlers()
  clearToasts()  // Add this
})
```

### Issue 5: MSW Handlers Not Working

**Problem**: Tests fail because API calls aren't being mocked.

**Cause**: MSW server not properly configured or handlers don't match URL.

**Solution**:
1. Verify server is started in `beforeAll`
2. Check handler URLs match exactly (including path params)
3. Verify `API_BASE_URL` is correct
4. Check MSW is imported from `msw/node`, not `msw`

## Summary

This role defines the technical **HOW** of writing unit tests for custom hooks:

1. **Setup**: Configure Vitest with jsdom environment and path aliases
2. **MSW**: Create reusable MSW handlers in `@/msw/resources/`
3. **Patterns**: Test success cases, error cases, return values, and side effects
4. **Toast Testing**: Verify toast notifications using store getters
5. **Best Practices**: Clean up state, use `waitFor`, and import types

**Key takeaway**: Always create MSW handlers in external resource files, never inline in tests. This ensures handlers can be reused across unit tests and Storybook stories.
