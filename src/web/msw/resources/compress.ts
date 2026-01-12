import { http, HttpResponse } from 'msw'

import { API_BASE_URL } from '@/constants/uri'
import type {
  CreateCompressorRequest,
  CreateCompressorResponse
} from '@/lib/api/session/compress'

/**
 * MSW handlers for /session/compress endpoints
 */
export const compressHandlers = [
  // POST /api/v1/session/compress
  http.post<never, CreateCompressorRequest, CreateCompressorResponse>(
    `${API_BASE_URL}/session/compress`,
    () =>
      HttpResponse.json({
        message: 'Compression started successfully',
        sessionId: 'test-compressor-session-id',
        summary: 'Test summary'
      })
  ),

  // POST /api/v1/session/compress/:compressorSessionId/approve
  http.post<{ compressorSessionId: string }, never, { message: string }>(
    `${API_BASE_URL}/session/compress/:compressorSessionId/approve`,
    () =>
      HttpResponse.json({
        message: 'Compression approved successfully'
      })
  ),

  // POST /api/v1/session/compress/:compressorSessionId/deny
  http.post<{ compressorSessionId: string }, never, { message: string }>(
    `${API_BASE_URL}/session/compress/:compressorSessionId/deny`,
    () =>
      HttpResponse.json({
        message: 'Compression denied successfully'
      })
  )
]

/**
 * MSW handlers for /session/compress endpoints with error responses
 */
export const compressErrorHandlers = [
  // POST /api/v1/session/compress (error response)
  http.post(
    `${API_BASE_URL}/session/compress`,
    () =>
      new HttpResponse(JSON.stringify({ message: 'Failed to start compression' }), {
        status: 500,
        headers: { 'Content-Type': 'application/json' }
      })
  ),

  // POST /api/v1/session/compress/:compressorSessionId/approve (error response)
  http.post(
    `${API_BASE_URL}/session/compress/:compressorSessionId/approve`,
    () =>
      new HttpResponse(JSON.stringify({ message: 'Failed to approve compression' }), {
        status: 500,
        headers: { 'Content-Type': 'application/json' }
      })
  ),

  // POST /api/v1/session/compress/:compressorSessionId/deny (error response)
  http.post(
    `${API_BASE_URL}/session/compress/:compressorSessionId/deny`,
    () =>
      new HttpResponse(JSON.stringify({ message: 'Failed to deny compression' }), {
        status: 500,
        headers: { 'Content-Type': 'application/json' }
      })
  )
]
