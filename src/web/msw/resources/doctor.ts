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
