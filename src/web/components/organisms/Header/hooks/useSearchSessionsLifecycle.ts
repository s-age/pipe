import { useEffect, useRef } from 'react'

export type UseSearchSessionsLifecycleProperties = {
  query: string
  fetchResults: (q: string) => Promise<unknown>
}

/**
 * useSearchSessionsLifecycle
 *
 * Manages SearchSessions lifecycle effects (debounced search).
 * Pattern: Lifecycle (separated from Handlers per hooks.md)
 */
export const useSearchSessionsLifecycle = ({
  query,
  fetchResults
}: UseSearchSessionsLifecycleProperties): void => {
  const timeoutIdReference = useRef<number | null>(null)

  useEffect(() => {
    if (timeoutIdReference.current) window.clearTimeout(timeoutIdReference.current)

    // setTimeout returns a platform-specific timer type; cast to the expected ReturnType
    // NOTE: casting because TS lib types for setTimeout may differ between DOM and Node.
    // This is safe in browser runtime.

    timeoutIdReference.current = window.setTimeout(() => fetchResults(query), 250)

    return (): void => {
      if (timeoutIdReference.current) {
        window.clearTimeout(timeoutIdReference.current)
      }
    }
  }, [query, fetchResults])
}
