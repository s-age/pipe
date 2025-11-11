import { useCallback } from 'react'
import type {
  ChangeEvent,
  KeyboardEvent as ReactKeyboardEvent,
  MouseEvent as ReactMouseEvent
} from 'react'

import type { SelectOption } from './useMultipleSelect'

type UseMultipleSelectHandlersProperties = {
  isOpen: boolean
  setIsOpen: (v: boolean) => void
  filteredOptions: SelectOption[]
  highlightedIndex: number
  setHighlightedIndex: (i: number) => void
  selectedValues: string[]
  setSelectedValues: (v: string[]) => void
  setQuery: (q: string) => void
}

export type UseMultipleSelectHandlersReturn = {
  toggleOpen: () => void
  handleToggleSelect: (value: string) => void
  handleRemoveTag: (event: React.MouseEvent) => void
  handleKeyDown: (event: KeyboardEvent) => void
  handleKeyDownReact: (event: ReactKeyboardEvent) => void
  handleSearchChange: (event: ChangeEvent<HTMLInputElement>) => void
  handleOptionClickReact: (event: ReactMouseEvent<HTMLLIElement>) => void
  handleMouseEnterReact: (event: ReactMouseEvent<HTMLLIElement>) => void
  handleMouseLeaveReact: () => void
}

export const useMultipleSelectHandlers = ({
  isOpen,
  setIsOpen,
  filteredOptions,
  highlightedIndex,
  setHighlightedIndex,
  selectedValues,
  setSelectedValues,
  setQuery
}: UseMultipleSelectHandlersProperties): UseMultipleSelectHandlersReturn => {
  const toggleOpen = useCallback(() => setIsOpen(!isOpen), [isOpen, setIsOpen])

  const handleToggleSelect = useCallback(
    (value: string) => {
      if (selectedValues.includes(value)) {
        setSelectedValues(selectedValues.filter((v) => v !== value))
      } else {
        setSelectedValues([...selectedValues, value])
      }
      // Don't close on select for multiple selection
      // setIsOpen(false)
      // setQuery('')
    },
    [selectedValues, setSelectedValues]
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
          handleToggleSelect(filteredOptions[highlightedIndex].value)
        }
      } else if (event.key === 'Escape') {
        setIsOpen(false)
      }
    },
    [
      isOpen,
      filteredOptions,
      highlightedIndex,
      handleToggleSelect,
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
      if (v) handleToggleSelect(v)
    },
    [handleToggleSelect]
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

  const handleRemoveTag = useCallback(
    (event: React.MouseEvent) => {
      const target = event.target as HTMLElement
      const index = target.closest('[data-index]')?.getAttribute('data-index')
      if (index !== null) {
        handleToggleSelect(selectedValues[Number(index)])
      }
    },
    [handleToggleSelect, selectedValues]
  )

  return {
    toggleOpen,
    handleToggleSelect,
    handleRemoveTag,
    handleKeyDown,
    handleKeyDownReact,
    handleSearchChange,
    handleOptionClickReact,
    handleMouseEnterReact,
    handleMouseLeaveReact
  }
}
