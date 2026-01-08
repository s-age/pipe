import { useCallback, useState } from 'react'
import type { MouseEvent, KeyboardEvent, Dispatch, SetStateAction } from 'react'

import { useFocusTrap } from '@/hooks/useFocusTrap'

import { useSearchSessionsActions } from './useSearchSessionsActions'
import { useSearchSessionsLifecycle } from './useSearchSessionsLifecycle'

type SearchResult = {
  sessionId: string
  title: string
}

type UseSearchSessionsHandlersReturn = {
  open: boolean
  query: string
  results: SearchResult[]
  setQuery: Dispatch<SetStateAction<string>>
  closeModal: () => void
  fetchResults: (q: string) => Promise<SearchResult[]>
  handleOverlayPointerDown: (event: MouseEvent<HTMLDivElement>) => void
  handleResultKeyDown: (event: KeyboardEvent<HTMLDivElement>) => void
  handleResultPointerDown: (event: MouseEvent<HTMLDivElement>) => void
  handleSelect: (id: string) => void
  handleSubmit: (value?: string) => Promise<void>
}

export const useSearchSessionsHandlers = (): UseSearchSessionsHandlersReturn => {
  const { executeSearch } = useSearchSessionsActions()

  const [query, setQuery] = useState('')
  const [results, setResults] = useState<SearchResult[]>([])
  const [open, setOpen] = useState(false)

  // Focus trap for modal
  useFocusTrap({ isOpen: open })

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

  // Lifecycle: debounced search
  useSearchSessionsLifecycle({ query, fetchResults })

  const handleSubmit = useCallback(
    async (_value?: string) => {
      const matches = await fetchResults(query)
      if (matches.length > 0) {
        window.location.href = `/session/${matches[0].sessionId}`
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
      const target = event.currentTarget

      // Type guard: verify target is HTMLElement
      if (!(target instanceof HTMLElement)) return

      const id = target.dataset.sessionId
      if (id) handleSelect(id)
    },
    [handleSelect]
  )

  const handleResultKeyDown = useCallback(
    (event: KeyboardEvent<HTMLDivElement>): void => {
      const target = event.currentTarget

      // Type guard: verify target is HTMLElement
      if (!(target instanceof HTMLElement)) return

      const id = target.dataset.sessionId
      if (!id) return
      if (event.key === 'Enter' || event.key === ' ') {
        event.preventDefault()
        handleSelect(id)
      }
      if (event.key === 'Escape') {
        event.preventDefault()
        closeModal()
      }
    },
    [handleSelect, closeModal]
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
