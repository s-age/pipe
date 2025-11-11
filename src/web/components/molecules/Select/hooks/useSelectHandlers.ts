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
  handleKeyDown: (event: KeyboardEvent) => void
  handleKeyDownReact: (event: ReactKeyboardEvent) => void
  handleSearchChange: (event: ChangeEvent<HTMLInputElement>) => void
  handleOptionClickReact: (event: ReactMouseEvent<HTMLLIElement>) => void
  handleMouseEnterReact: (event: ReactMouseEvent<HTMLLIElement>) => void
  handleMouseLeaveReact: () => void
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

  const handleKeyDown = useCallback(
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
          handleSelect(filteredOptions[highlightedIndex].value)
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

  const handleKeyDownReact = useCallback(
    (event: ReactKeyboardEvent) => handleKeyDown(event.nativeEvent as KeyboardEvent),
    [handleKeyDown]
  )

  const handleSearchChange = useCallback(
    (event: ChangeEvent<HTMLInputElement>) => setQuery(event.target.value),
    [setQuery]
  )

  const handleOptionClickReact = useCallback(
    (event: ReactMouseEvent<HTMLLIElement>) => {
      const v = (event.currentTarget as HTMLElement).dataset.value
      if (v) handleSelect(v)
    },
    [handleSelect]
  )

  const handleMouseEnterReact = useCallback(
    (event: ReactMouseEvent<HTMLLIElement>) => {
      const index_ = (event.currentTarget as HTMLElement).dataset.index
      if (index_) setHighlightedIndex(Number(index_))
    },
    [setHighlightedIndex]
  )

  const handleMouseLeaveReact = useCallback(
    () => setHighlightedIndex(-1),
    [setHighlightedIndex]
  )

  return {
    toggleOpen,
    handleSelect,
    handleKeyDown,
    handleKeyDownReact,
    handleSearchChange,
    handleOptionClickReact,
    handleMouseEnterReact,
    handleMouseLeaveReact
  }
}
