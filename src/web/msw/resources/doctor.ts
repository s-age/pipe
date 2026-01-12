import { http, HttpResponse, delay } from 'msw'

import { API_BASE_URL } from '@/constants/uri'

/**
 * MSW handlers for /doctor endpoints
 */
export const doctorHandlers = [
  // POST /api/v1/doctor
  http.post(`${API_BASE_URL}/doctor`, () =>
    HttpResponse.json({
      result: { status: 'Succeeded' },
      sessionId: 'test-session-id'
    })
  )
]

/**
 * MSW handlers for /doctor endpoints with delay
 */
export const doctorDelayHandlers = [
  // POST /api/v1/doctor (with 500ms delay)
  http.post(`${API_BASE_URL}/doctor`, async () => {
    await delay(500)

    return HttpResponse.json({
      result: { status: 'Succeeded' },
      sessionId: 'session-1234567890'
    })
  })
]

/**
 * MSW handlers for /doctor endpoints with error responses
 */
export const doctorErrorHandlers = [
  // POST /api/v1/doctor (error response)
  http.post(
    `${API_BASE_URL}/doctor`,
    () =>
      new HttpResponse(JSON.stringify({ message: 'Failed to apply modifications' }), {
        status: 500,
        headers: { 'Content-Type': 'application/json' }
      })
  ),

  // POST /api/v1/doctor (failed status response)
  http.post(`${API_BASE_URL}/doctor`, () =>
    HttpResponse.json({
      result: { status: 'Failed', reason: 'Validation error' },
      sessionId: 'test-session-id'
    })
  )
]
