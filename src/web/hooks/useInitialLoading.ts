import { useEffect, useRef } from 'react'

/**
 * Execute an async function only once on initial mount, even in StrictMode.
 * Prevents duplicate API calls during React StrictMode's double-invocation.
 *
 * @param loadFunction - Async function to execute on initial mount
 *
 * @example
 * ```tsx
 * useInitialLoading(async () => {
 *   const data = await fetchData()
 *   setData(data)
 * })
 * ```
 */
export const useInitialLoading = (loadFunction: () => Promise<void>): void => {
  const initializedReference = useRef(false)

  useEffect(() => {
    // Prevent duplicate execution in StrictMode
    if (initializedReference.current) {
      return
    }

    initializedReference.current = true
    void loadFunction()
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])
}
