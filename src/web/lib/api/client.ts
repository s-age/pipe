/**
 * client.ts
 *
 * This file provides a set of utility functions for making HTTP requests
 * (GET, POST, PATCH, DELETE) using the native Fetch API.
 * It handles JSON serialization and deserialization, and provides a consistent
 * interface for interacting with RESTful APIs.
 */

import { API_BASE_URL } from '@/constants/uri'

type RequestOptions = Omit<RequestInit, 'body'> & {
  body?: Record<string, unknown>
}

const request = async <T>(
  method: string,
  url: string,
  options?: RequestOptions
): Promise<T> => {
  const headers = {
    'Content-Type': 'application/json',
    ...options?.headers
  }

  const config: Omit<RequestInit, 'body'> & { body?: BodyInit | null } = {
    method,
    headers,
    ...options,
    body: options?.body ? JSON.stringify(options.body) : undefined
  }

  const response = await fetch(url, config)

  if (!response.ok) {
    const contentType = response.headers.get('content-type')
    let errorMessage = 'Something went wrong'

    if (contentType && contentType.includes('application/json')) {
      const errorData = await response
        .json()
        .catch(() => ({ message: response.statusText }))
      errorMessage = errorData.message || response.statusText
    } else {
      errorMessage = await response.text()
    }
    throw new Error(errorMessage)
  }

  // Handle cases where the response might not have a body (e.g., 204 No Content)
  if (response.status === 204) {
    return {} as T
  }

  const json = await response.json()

  // If response follows new API format {success, data, message}, extract data
  if (json && typeof json === 'object' && 'data' in json) {
    // Return the data field directly, even if it's null
    // The caller should handle null/undefined cases
    return json.data as T
  }

  // For responses without 'data' field, return the whole response
  return json as T
}

export const client = {
  get: <T>(url: string, options?: RequestOptions): Promise<T> =>
    request<T>('GET', `${API_BASE_URL}${url}`, options),

  post: <T>(url: string, options?: RequestOptions): Promise<T> =>
    request<T>('POST', `${API_BASE_URL}${url}`, options),

  patch: <T>(url: string, options?: RequestOptions): Promise<T> =>
    request<T>('PATCH', `${API_BASE_URL}${url}`, options),

  delete: <T>(url: string, options?: RequestOptions): Promise<T> =>
    request<T>('DELETE', `${API_BASE_URL}${url}`, options)
}
