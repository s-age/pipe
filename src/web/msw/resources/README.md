# MSW Resources

This directory contains MSW (Mock Service Worker) handlers organized by resource for use in Storybook.

## Directory Structure

```
msw/resources/
├── README.md
├── fs.ts          # Endpoints for /api/v1/fs/*
├── session.ts     # Endpoints for /api/v1/session/* (example)
└── user.ts        # Endpoints for /api/v1/user/* (example)
```

## File Naming Convention

File names should match the **first element** of the pathname that follows `/api/v1`, split by slashes.

### Examples

| Endpoint                 | File Name    |
| ------------------------ | ------------ |
| `/api/v1/fs/search`      | `fs.ts`      |
| `/api/v1/fs/delete`      | `fs.ts`      |
| `/api/v1/session/create` | `session.ts` |
| `/api/v1/session/list`   | `session.ts` |
| `/api/v1/user/profile`   | `user.ts`    |

## File Structure

Each file should follow this structure:

```typescript
import { http, HttpResponse } from 'msw'

import { API_BASE_URL } from '@/constants/uri'
import type { YourResponseType } from '@/lib/api/your/endpoint'

/**
 * MSW handlers for /{resource} endpoints
 */
export const {resource}Handlers = [
  // GET /api/v1/{resource}/{action}
  http.get<never, never, YourResponseType>(
    `${API_BASE_URL}/{resource}/{action}`,
    () => {
      return HttpResponse.json({
        // Mock response
      })
    }
  ),

  // POST /api/v1/{resource}/{action}
  http.post<never, YourRequestType, YourResponseType>(
    `${API_BASE_URL}/{resource}/{action}`,
    async ({ request }) => {
      const body = await request.json()

      return HttpResponse.json({
        // Mock response
      })
    }
  )
]
```

## Usage

Use handlers in Storybook story files like this:

```typescript
import { fsHandlers } from '@/msw/resources/fs'

export const YourStory: Story = {
  parameters: {
    msw: {
      handlers: fsHandlers
    }
  }
  // ...
}
```

## Guidelines

- Always import `API_BASE_URL` from `@/constants/uri`
- Reuse type definitions from corresponding API client files (`@/lib/api/*`)
- Add descriptive comments for each handler
- Export handler arrays using the naming pattern `{resource}Handlers`
