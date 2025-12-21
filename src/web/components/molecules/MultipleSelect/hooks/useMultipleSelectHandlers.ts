import { useCallback } from 'react'
import type {
  ChangeEvent,
  Dispatch,
  KeyboardEvent as ReactKeyboardEvent,
  MouseEvent as ReactMouseEvent,
  SetStateAction
} from 'react'

import type { SelectOption } from './useMultipleSelect'

type UseMultipleSelectHandlersProperties = {
  isOpen: boolean
  setIsOpen: (v: boolean) => void
  filteredOptions: SelectOption[]
  highlightedIndex: number
  setHighlightedIndex: (i: number) => void
  selectedValues: string[]
  setSelectedValues: Dispatch<SetStateAction<string[]>>
  setQuery: (q: string) => void
}

export type UseMultipleSelectHandlersReturn = {
  toggleOpen: () => void
  handleToggleSelect: (value: string) => void
  handleRemoveTag: (event: React.MouseEvent) => void
  handleKeyDown: (event: ReactKeyboardEvent) => void
  handleSearchChange: (event: ChangeEvent<HTMLInputElement>) => void
  handleOptionClick: (event: ReactMouseEvent<HTMLLIElement>) => void
  handleMouseEnter: (event: ReactMouseEvent<HTMLLIElement>) => void
  handleMouseLeave: () => void
  handleCheckboxClick: (event: ReactMouseEvent<HTMLInputElement>) => void
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
      setSelectedValues((previous) => {
        let next: string[]
        if (previous.includes(value)) {
          next = previous.filter((v) => v !== value)
        } else {
          next = [...previous, value]
        }

        return next
      })
      // Don't close on select for multiple selection
      // setIsOpen(false)
      // setQuery('')
    },
    [setSelectedValues]
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

  const handleKeyDown = useCallback(
    (event: ReactKeyboardEvent) => {
      // Type guard: verify nativeEvent is KeyboardEvent
      if (event.nativeEvent instanceof KeyboardEvent) {
        handleKeyDownNative(event.nativeEvent)
      }
    },
    [handleKeyDownNative]
  )

  const handleSearchChange = useCallback(
    (event: ChangeEvent<HTMLInputElement>) => setQuery(event.target.value),
    [setQuery]
  )

  const handleOptionClick = useCallback(
    (event: ReactMouseEvent<HTMLLIElement>) => {
      // Prevent outer click handlers from reacting to this selection click
      event.stopPropagation()
      const target = event.currentTarget

      // Type guard: verify target is HTMLElement
      if (!(target instanceof HTMLElement)) return

      const v = target.dataset.value
      // debug logs removed
      // Allow empty-string values (dataset returns '' for empty), reject only undefined
      if (v !== undefined) handleToggleSelect(v)
    },
    [handleToggleSelect]
  )

  const handleMouseEnter = useCallback(
    (event: ReactMouseEvent<HTMLLIElement>) => {
      const target = event.currentTarget

      // Type guard: verify target is HTMLElement
      if (!(target instanceof HTMLElement)) return

      const index_ = target.dataset.index
      if (index_) setHighlightedIndex(Number(index_))
    },
    [setHighlightedIndex]
  )

  const handleMouseLeave = useCallback(
    () => setHighlightedIndex(-1),
    [setHighlightedIndex]
  )

  const handleRemoveTag = useCallback(
    (event: React.MouseEvent) => {
      const target = event.target

      // Type guard: verify target is HTMLElement
      if (!(target instanceof HTMLElement)) return

      const index = target.closest('[data-index]')?.getAttribute('data-index')
      if (index !== null) {
        handleToggleSelect(selectedValues[Number(index)])
      }
    },
    [handleToggleSelect, selectedValues]
  )

  const handleCheckboxClick = useCallback(
    (event: ReactMouseEvent<HTMLInputElement>) => {
      event.stopPropagation()
      const target = event.currentTarget

      // Type guard: verify target is HTMLInputElement
      if (!(target instanceof HTMLInputElement)) return

      const value = target.value
      handleToggleSelect(value)
    },
    [handleToggleSelect]
  )

  return {
    toggleOpen,
    handleToggleSelect,
    handleRemoveTag,
    handleKeyDown,
    handleSearchChange,
    handleOptionClick,
    handleMouseEnter,
    handleMouseLeave,
    handleCheckboxClick
  }
}
