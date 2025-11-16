import { useCallback } from 'react'
import type {
  ChangeEvent,
  KeyboardEvent as ReactKeyboardEvent,
  MouseEvent as ReactMouseEvent
} from 'react'

import type { SelectOption } from './useSelect'

type UseSelectHandlersProperties = {
  isOpen: boolean
  setIsOpen: (v: boolean) => void
  filteredOptions: SelectOption[]
  highlightedIndex: number
  setHighlightedIndex: (i: number) => void
  setSelectedValue: (v: string) => void
  setQuery: (q: string) => void
}

export type UseSelectHandlersReturn = {
  toggleOpen: () => void
  handleSelect: (value: string) => void
  handleKeyDown: (event: ReactKeyboardEvent) => void
  handleSearchChange: (event: ChangeEvent<HTMLInputElement>) => void
  handleOptionClick: (event: ReactMouseEvent<HTMLLIElement>) => void
  handleMouseEnter: (event: ReactMouseEvent<HTMLLIElement>) => void
  handleMouseLeave: () => void
}

export const useSelectHandlers = ({
  isOpen,
  setIsOpen,
  filteredOptions,
  highlightedIndex,
  setHighlightedIndex,
  setSelectedValue,
  setQuery
}: UseSelectHandlersProperties): UseSelectHandlersReturn => {
  const toggleOpen = useCallback(() => setIsOpen(!isOpen), [isOpen, setIsOpen])

  const handleSelect = useCallback(
    (value: string) => {
      setSelectedValue(value)
      setIsOpen(false)
      setQuery('')
    },
    [setSelectedValue, setIsOpen, setQuery]
  )

  const handleKeyDownNative = useCallback(
    (event: KeyboardEvent) => {
      if (!isOpen) return

      if (event.key === 'ArrowDown') {
        event.preventDefault()
        setHighlightedIndex(Math.min(highlightedIndex + 1, filteredOptions.length - 1))
      } else if (event.key === 'ArrowUp') {
        event.preventDefault()
        setHighlightedIndex(Math.max(highlightedIndex - 1, 0))
      } else if (event.key === 'Enter') {
        event.preventDefault()
        if (highlightedIndex >= 0 && highlightedIndex < filteredOptions.length) {
          handleSelect(
            filteredOptions[highlightedIndex].id ??
              filteredOptions[highlightedIndex].value
          )
        }
      } else if (event.key === 'Escape') {
        setIsOpen(false)
      }
    },
    [
      isOpen,
      filteredOptions,
      highlightedIndex,
      handleSelect,
      setHighlightedIndex,
      setIsOpen
    ]
  )

  const handleKeyDown = useCallback(
    (event: ReactKeyboardEvent) =>
      handleKeyDownNative(event.nativeEvent as KeyboardEvent),
    [handleKeyDownNative]
  )

  const handleSearchChange = useCallback(
    (event: ChangeEvent<HTMLInputElement>) => setQuery(event.target.value),
    [setQuery]
  )

  const handleOptionClick = useCallback(
    (event: ReactMouseEvent<HTMLLIElement>) => {
      // Prefer using the dataset index (reliable mapping to filteredOptions)
      const indexString = (event.currentTarget as HTMLElement).dataset.index
      if (indexString) {
        const i = Number(indexString)
        const opt = filteredOptions[i]
        if (opt) {
          // Diagnostic: log click mapping info so developer console shows actions
          // click mapping (diagnostics removed)
          handleSelect(opt.id ?? opt.value)

          return
        }
      }

      // Fallback: map by internal id or value
      const v = (event.currentTarget as HTMLElement).dataset.value

      // fallback mapping (diagnostics removed)
      if (v === undefined) return
      const opt2 = filteredOptions.find((o) => o.id === v || o.value === v)

      // fallback resolvedOpt (diagnostics removed)
      if (opt2) handleSelect(opt2.id ?? opt2.value)
    },
    [handleSelect, filteredOptions]
  )

  const handleMouseEnter = useCallback(
    (event: ReactMouseEvent<HTMLLIElement>) => {
      const index_ = (event.currentTarget as HTMLElement).dataset.index
      if (index_) setHighlightedIndex(Number(index_))
    },
    [setHighlightedIndex]
  )

  const handleMouseLeave = useCallback(
    () => setHighlightedIndex(-1),
    [setHighlightedIndex]
  )

  return {
    toggleOpen,
    handleSelect,
    handleKeyDown,
    handleSearchChange,
    handleOptionClick,
    handleMouseEnter,
    handleMouseLeave
  }
}
