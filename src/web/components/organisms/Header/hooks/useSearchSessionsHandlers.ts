import { useCallback, useEffect, useRef, useState } from 'react'
import type { MouseEvent, KeyboardEvent, Dispatch, SetStateAction } from 'react'

import { useSearchSessionsActions } from './useSearchSessionsActions'

type SearchResult = {
  session_id: string
  title: string
}

type UseSearchSessionsHandlersReturn = {
  query: string
  setQuery: Dispatch<SetStateAction<string>>
  results: SearchResult[]
  open: boolean
  fetchResults: (q: string) => Promise<SearchResult[]>
  handleSubmit: (value?: string) => Promise<void>
  handleSelect: (id: string) => void
  closeModal: () => void
  handleOverlayPointerDown: (event: MouseEvent<HTMLDivElement>) => void
  handleResultPointerDown: (event: MouseEvent<HTMLDivElement>) => void
  handleResultKeyDown: (event: KeyboardEvent<HTMLDivElement>) => void
}

export const useSearchSessionsHandlers = (): UseSearchSessionsHandlersReturn => {
  const { executeSearch } = useSearchSessionsActions()

  const [query, setQuery] = useState('')
  const [results, setResults] = useState<SearchResult[]>([])
  const [open, setOpen] = useState(false)
  const timeoutIdReference = useRef<ReturnType<typeof window.setTimeout> | null>(null)

  const fetchResults = useCallback(
    async (q: string) => {
      if (!q || !q.trim()) {
        setResults([])
        setOpen(false)

        return [] as SearchResult[]
      }

      const matches = await executeSearch(q)
      setResults(matches)
      setOpen(matches.length > 0)

      return matches
    },
    [executeSearch]
  )

  useEffect(() => {
    if (timeoutIdReference.current) window.clearTimeout(timeoutIdReference.current)

    // setTimeout returns a platform-specific timer type; cast to the expected ReturnType
    // NOTE: casting because TS lib types for setTimeout may differ between DOM and Node.
    // This is safe in browser runtime.

    timeoutIdReference.current = window.setTimeout(
      () => fetchResults(query),
      250
    ) as unknown as ReturnType<typeof setTimeout>

    return (): void => {
      if (timeoutIdReference.current)
        window.clearTimeout(timeoutIdReference.current as unknown as number)
    }
  }, [query, fetchResults])

  const handleSubmit = useCallback(
    async (_value?: string) => {
      const matches = await fetchResults(query)
      if (matches.length > 0) {
        window.location.href = `/session/${matches[0].session_id}`
      } else {
        setOpen(true)
      }
    },
    [fetchResults, query]
  )

  const handleSelect = useCallback((id: string) => {
    window.location.href = `/session/${id}`
  }, [])

  const closeModal = useCallback(() => setOpen(false), [])

  const handleOverlayPointerDown = useCallback(
    (event: MouseEvent<HTMLDivElement>): void => {
      if (event.target === event.currentTarget) closeModal()
    },
    [closeModal]
  )

  const handleResultPointerDown = useCallback(
    (event: MouseEvent<HTMLDivElement>): void => {
      const id = (event.currentTarget as HTMLElement).dataset.sessionId
      if (id) handleSelect(id)
    },
    [handleSelect]
  )

  const handleResultKeyDown = useCallback(
    (event: KeyboardEvent<HTMLDivElement>): void => {
      const id = (event.currentTarget as HTMLElement).dataset.sessionId
      if (!id) return
      if (event.key === 'Enter' || event.key === ' ') handleSelect(id)
    },
    [handleSelect]
  )

  return {
    query,
    setQuery,
    results,
    open,
    fetchResults,
    handleSubmit,
    handleSelect,
    closeModal,
    handleOverlayPointerDown,
    handleResultPointerDown,
    handleResultKeyDown
  }
}
