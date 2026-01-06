/**
 * streamingClient.ts
 *
 * This file provides a utility for making streaming HTTP requests.
 * Unlike the regular client.ts which handles JSON responses,
 * this client returns ReadableStream for Server-Sent Events and
 * streaming text responses.
 */

export const API_BASE_URL = 'http://localhost:5001/api/v1'

type StreamingRequestOptions = {
  body?: Record<string, unknown>
  headers?: HeadersInit
  signal?: AbortSignal
}

const streamingRequest = async (
  method: string,
  url: string,
  options?: StreamingRequestOptions
): Promise<ReadableStream<Uint8Array>> => {
  const headers = {
    'Content-Type': 'application/json',
    ...options?.headers
  }

  const response = await fetch(url, {
    method,
    headers,
    body: options?.body ? JSON.stringify(options.body) : undefined,
    signal: options?.signal
  })

  if (!response.ok) {
    const contentType = response.headers.get('content-type')
    let errorMessage = 'Streaming request failed'

    if (contentType?.includes('application/json')) {
      const errorData = await response
        .json()
        .catch(() => ({ message: response.statusText }))
      errorMessage = errorData.message || response.statusText
    } else {
      errorMessage = await response.text()
    }
    throw new Error(errorMessage)
  }

  if (!response.body) {
    throw new Error('Response body is empty')
  }

  return response.body
}

export const streamingClient = {
  post: (
    url: string,
    options?: StreamingRequestOptions
  ): Promise<ReadableStream<Uint8Array>> =>
    streamingRequest('POST', `${API_BASE_URL}${url}`, options)
}
