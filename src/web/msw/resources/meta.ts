import { http, HttpResponse } from 'msw'

import { API_BASE_URL } from '@/constants/uri'

/**
 * MSW handlers for /meta endpoints
 */
export const metaHandlers = [
  // POST /api/v1/meta/hyperparameters/:sessionId
  http.post(`${API_BASE_URL}/meta/hyperparameters/:sessionId`, async ({ params }) =>
    HttpResponse.json({
      message: 'Hyperparameters updated successfully',
      session: {
        sessionId: params.sessionId as string,
        hyperparameters: {
          temperature: 0.7,
          topP: 0.9,
          topK: 5
        }
      }
    })
  )
]
