import { http, HttpResponse, delay } from 'msw'

import { API_BASE_URL } from '@/constants/uri'

/**
 * MSW handlers for /therapist endpoints
 */
export const therapistHandlers = [
  // POST /api/v1/therapist
  http.post(`${API_BASE_URL}/therapist`, () =>
    HttpResponse.json({
      diagnosis: {
        summary:
          'The session contains some redundant turns and could be improved by editing turn 2.',
        deletions: [1],
        edits: [{ turn: 2, newContent: 'Improved content for turn 2' }],
        compressions: [{ start: 1, end: 2, reason: 'Redundant interaction' }],
        rawDiagnosis: 'Raw diagnosis data for debugging'
      },
      sessionId: 'test-session-id'
    })
  )
]

/**
 * MSW handlers for /therapist endpoints with delay
 */
export const therapistDelayHandlers = [
  // POST /api/v1/therapist (with 500ms delay)
  http.post(`${API_BASE_URL}/therapist`, async () => {
    await delay(500)

    return HttpResponse.json({
      diagnosis: {
        summary:
          'The session contains some redundant turns and could be improved by editing turn 2.',
        deletions: [1],
        edits: [{ turn: 2, newContent: 'Improved content for turn 2' }],
        compressions: [{ start: 1, end: 2, reason: 'Redundant interaction' }],
        rawDiagnosis: 'Raw diagnosis data for debugging'
      },
      sessionId: 'session-1234567890'
    })
  })
]

/**
 * MSW handlers for /therapist endpoints with empty diagnosis results
 */
export const therapistEmptyHandlers = [
  // POST /api/v1/therapist (empty diagnosis)
  http.post(`${API_BASE_URL}/therapist`, () =>
    HttpResponse.json({
      diagnosis: {
        summary: 'No issues found in the session.',
        deletions: null,
        edits: null,
        compressions: null,
        rawDiagnosis: 'No modifications needed'
      },
      sessionId: 'session-1234567890'
    })
  )
]

/**
 * MSW handlers for /therapist endpoints with error responses
 */
export const therapistErrorHandlers = [
  // POST /api/v1/therapist (error response)
  http.post(`${API_BASE_URL}/therapist`, () =>
    new HttpResponse(JSON.stringify({ message: 'Diagnosis failed' }), {
      status: 500,
      headers: { 'Content-Type': 'application/json' }
    })
  )
]
