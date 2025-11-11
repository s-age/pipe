# API Guidelines

## Overview

All API functions in this project must use the centralized `client` from `@/lib/api/client`. This ensures consistent error handling, request formatting, and response processing across the application.

## Core Principles

1. **Always use `client`** - Never use `fetch` directly in API functions
2. **No exception handling** - Let errors propagate to the calling code (Actions hooks)
3. **Type everything** - Define request/response types explicitly
4. **One function per endpoint** - Keep API functions focused and simple

## The Client

The `client` provides four HTTP methods:

```typescript
import { client } from '@/lib/api/client'

// GET request
client.get<ResponseType>(url, options?)

// POST request
client.post<ResponseType>(url, options?)

// PATCH request
client.patch<ResponseType>(url, options?)

// DELETE request
client.delete<ResponseType>(url, options?)
```

### Features

- **Automatic JSON serialization/deserialization**
- **Consistent error handling** - Throws errors with server messages
- **Type-safe** - Generic type parameter for response
- **Automatic base URL** - Prepends `API_BASE_URL` to all requests

## HTTP Methods

### GET - Retrieve Data

Use `GET` for fetching data without side effects.

```typescript
import { client } from '../client'

export type SessionDetail = {
  id: string
  purpose: string
  background: string
  // ... other fields
}

export const getSession = async (
  sessionId: string
): Promise<{ session: SessionDetail }> =>
  client.get<{ session: SessionDetail }>(`/session/${sessionId}`)
```

**When to use GET:**

- ✅ Fetching a single resource
- ✅ Fetching a list of resources
- ✅ Querying data
- ❌ Creating, updating, or deleting data

### POST - Create Resources

Use `POST` for creating new resources or triggering actions.

```typescript
import { client } from '../client'

export type StartSessionRequest = {
  purpose: string
  background: string
  instruction: string
  roles: string[] | null
  // ... other fields
}

export const startSession = async (
  data: StartSessionRequest
): Promise<{ session_id: string }> =>
  client.post<{ session_id: string }>(`/sessions/start`, {
    body: data
  })
```

**When to use POST:**

- ✅ Creating a new resource
- ✅ Triggering an action (start session, send instruction)
- ✅ Submitting form data
- ❌ Updating existing resources (use PATCH)

### PATCH - Update Resources

Use `PATCH` for partial updates to existing resources.

```typescript
import { client } from '../client'

export type EditSessionMetaRequest = {
  purpose?: string
  background?: string
  roles?: string[] | null
  // ... other optional fields
}

export const editSessionMeta = async (
  sessionId: string,
  meta: EditSessionMetaRequest
): Promise<{ message: string }> =>
  client.patch<{ message: string }>(`/session/${sessionId}/meta`, {
    body: meta
  })
```

**When to use PATCH:**

- ✅ Updating part of a resource
- ✅ Modifying specific fields
- ✅ Optional/partial updates
- ❌ Creating resources (use POST)
- ❌ Replacing entire resource (use PUT if needed)

### DELETE - Remove Resources

Use `DELETE` for removing resources.

```typescript
import { client } from '../client'

export const deleteSession = async (sessionId: string): Promise<void> => {
  await client.delete<void>(`/session/${sessionId}`)
}
```

**When to use DELETE:**

- ✅ Removing a resource
- ✅ Canceling an operation
- ❌ Updating resources (use PATCH)

## File Structure

Organize API functions by domain:

```
src/web/lib/api/
├── client.ts              # HTTP client (don't modify)
├── session/
│   ├── getSession.ts      # GET /session/:id
│   ├── startSession.ts    # POST /sessions/start
│   ├── editSessionMeta.ts # PATCH /session/:id/meta
│   ├── deleteSession.ts   # DELETE /session/:id
│   └── ...
├── sessionTree/
│   └── getSessionTree.ts  # GET /session-tree
└── bff/
    └── getSessionDashboard.ts  # GET /session-dashboard
```

**Naming conventions:**

- `get{Resource}` - GET endpoints
- `edit{Resource}` - PATCH endpoints
- `delete{Resource}` - DELETE endpoints
- `start{Action}`, `send{Action}` - POST endpoints for actions

## Type Definitions

### Export Request Types

Always export request types when the API accepts a body:

```typescript
export type EditSessionMetaRequest = {
  purpose?: string
  background?: string
  roles?: string[] | null
}

export const editSessionMeta = async (
  sessionId: string,
  meta: EditSessionMetaRequest
): Promise<{ message: string }> => {
  // ...
}
```

### Export Response Types

Export complex response types for reuse:

```typescript
export type SessionDetail = {
  id: string
  purpose: string
  // ... fields
}

export const getSession = async (
  sessionId: string
): Promise<{ session: SessionDetail }> => {
  // ...
}
```

### Optional vs Required Fields

Use TypeScript's optional fields (`?`) to match the API contract:

```typescript
// All fields optional for partial updates
export type EditSessionMetaRequest = {
  purpose?: string
  background?: string
  roles?: string[] | null // null to clear, undefined to skip
}

// Required fields for creation
export type StartSessionRequest = {
  purpose: string // required
  background: string // required
  roles: string[] | null // required but nullable
}
```

## Error Handling

**Do NOT handle errors in API functions.** The `client` automatically:

1. Throws errors for non-OK responses
2. Extracts error messages from the response
3. Provides consistent error format

```typescript
// ✅ Correct - Let errors propagate
export const getSession = async (
  sessionId: string
): Promise<{ session: SessionDetail }> =>
  client.get<{ session: SessionDetail }>(`/session/${sessionId}`)

// ❌ Wrong - Don't catch errors here
export const getSession = async (
  sessionId: string
): Promise<{ session: SessionDetail }> => {
  try {
    return await client.get<{ session: SessionDetail }>(`/session/${sessionId}`)
  } catch (error) {
    console.error(error) // Don't do this
    throw error
  }
}
```

**Error handling belongs in Actions hooks:**

```typescript
// In useSessionActions.ts
export const useSessionActions = () => {
  const toast = useToast()

  const loadSession = useCallback(
    async (sessionId: string) => {
      try {
        const result = await getSession(sessionId) // API call
        toast.success('Session loaded')
        return result
      } catch (error: unknown) {
        toast.failure((error as Error).message) // Handle here
        throw error
      }
    },
    [toast]
  )

  return { loadSession }
}
```

## Complete Examples

### GET Example

```typescript
import type { SessionTree } from '@/types/sessionTree'
import { client } from '../client'

export const getSessionTree = async (): Promise<SessionTree> =>
  client.get<SessionTree>('/session-tree')
```

### POST Example

```typescript
import { client } from '../client'

export type SendInstructionRequest = {
  instruction: string
  stream?: boolean
}

export const sendInstruction = async (
  sessionId: string,
  data: SendInstructionRequest
): Promise<{ message: string }> =>
  client.post<{ message: string }>(`/session/${sessionId}/instruction`, {
    body: data
  })
```

### PATCH Example

```typescript
import { client } from '../client'

export type EditTodoRequest = {
  todo_id: string
  title?: string
  completed?: boolean
}

export const editTodo = async (
  sessionId: string,
  data: EditTodoRequest
): Promise<{ message: string; todo: Todo }> =>
  client.patch<{ message: string; todo: Todo }>(
    `/session/${sessionId}/todos/${data.todo_id}`,
    { body: data }
  )
```

### DELETE Example

```typescript
import { client } from '../client'

export const deleteTurn = async (
  sessionId: string,
  turnIndex: number
): Promise<{ message: string }> =>
  client.delete<{ message: string }>(`/session/${sessionId}/turns/${turnIndex}`)
```

## URL Construction

### Path Parameters

Include path parameters as function arguments:

```typescript
// ✅ Good - sessionId as parameter
export const getSession = async (sessionId: string) =>
  client.get(`/session/${sessionId}`)

// ❌ Bad - hardcoded ID
export const getSession = async () => client.get(`/session/123`)
```

### Query Parameters

Use the `options` parameter for query strings (if needed):

```typescript
export const getSessions = async (filters?: { limit?: number; offset?: number }) => {
  const params = new URLSearchParams()
  if (filters?.limit) params.append('limit', String(filters.limit))
  if (filters?.offset) params.append('offset', String(filters.offset))

  const query = params.toString()
  return client.get(`/sessions${query ? `?${query}` : ''}`)
}
```

## Best Practices

1. **Keep it simple** - API functions should be thin wrappers
2. **One function per endpoint** - Don't combine multiple endpoints
3. **Export types** - Make request/response types reusable
4. **Use TypeScript strictly** - No `any` types
5. **Arrow functions** - Use concise arrow function syntax
6. **Async/await** - Always mark as `async` and return promises
7. **No side effects** - No logging, no state changes, no error handling
8. **Descriptive names** - Function names should describe the operation

## Testing API Functions

API functions are typically tested through Actions hooks, but you can test them directly:

```typescript
import { getSession } from './getSession'
import { client } from '../client'

jest.mock('../client')

describe('getSession', () => {
  it('calls client.get with correct URL', async () => {
    const mockResponse = { session: { id: '123', purpose: 'test' } }
    ;(client.get as jest.Mock).mockResolvedValue(mockResponse)

    const result = await getSession('123')

    expect(client.get).toHaveBeenCalledWith('/session/123')
    expect(result).toEqual(mockResponse)
  })
})
```

## Common Patterns

### Void Response

For operations that don't return data:

```typescript
export const deleteSession = async (sessionId: string): Promise<void> => {
  await client.delete<void>(`/session/${sessionId}`)
}
```

### Message Response

For operations that return a success message:

```typescript
export const editSessionMeta = async (
  sessionId: string,
  meta: EditSessionMetaRequest
): Promise<{ message: string }> =>
  client.patch<{ message: string }>(`/session/${sessionId}/meta`, {
    body: meta
  })
```

### Resource Response

For operations that return the created/updated resource:

```typescript
export const startSession = async (
  data: StartSessionRequest
): Promise<{ session_id: string }> =>
  client.post<{ session_id: string }>(`/sessions/start`, {
    body: data
  })
```

## Related Documentation

- [Custom Hooks Guidelines](./hooks/hooks.md) - How to use API functions in hooks
- [Actions Pattern](./hooks/useActions.md) - Wrapping API calls with error handling
