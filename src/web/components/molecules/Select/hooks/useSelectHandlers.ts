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
  onChange?: (event: ChangeEvent<HTMLSelectElement>) => void
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
  setQuery,
  onChange
}: UseSelectHandlersProperties): UseSelectHandlersReturn => {
  const toggleOpen = useCallback(() => setIsOpen(!isOpen), [isOpen, setIsOpen])

  const handleSelect = useCallback(
    (value: string) => {
      setSelectedValue(value)
      setIsOpen(false)
      setQuery('')

      // Trigger onChange callback if provided
      if (onChange) {
        const syntheticEvent = {
          target: { value },
          currentTarget: { value }
        } as ChangeEvent<HTMLSelectElement>
        onChange(syntheticEvent)
      }
    },
    [setSelectedValue, setIsOpen, setQuery, onChange]
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
      const target = event.currentTarget

      // Type guard: verify target is HTMLElement
      if (!(target instanceof HTMLElement)) return

      // Prefer using the dataset index (reliable mapping to filteredOptions)
      const indexString = target.dataset.index
      if (indexString) {
        const i = Number(indexString)
        const opt = filteredOptions[i]
        if (opt) {
          handleSelect(opt.id ?? opt.value)

          return
        }
      }

      // Fallback: map by internal id or value
      const v = target.dataset.value

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
