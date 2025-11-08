import { useCallback, useMemo, useState, useRef } from 'react'
import type {
  FieldValues,
  UseFormRegister,
  UseFormRegisterReturn,
} from 'react-hook-form'

import type { FormMethods } from '@/components/organisms/Form'
import { useOptionalFormContext } from '@/components/organisms/Form'

export type SelectOption = { value: string; label: React.ReactNode }

type UseSelectProperties = {
  register?: UseFormRegister<FieldValues>
  name?: string
  options?: Array<string | SelectOption>
  defaultValue?: string
  searchable?: boolean
}

export type UseSelectReturn = {
  registerProperties: Partial<UseFormRegisterReturn>
  normalizedOptions: SelectOption[]
  filteredOptions: SelectOption[]
  query: string
  setQuery: (q: string) => void
  isOpen: boolean
  setIsOpen: (v: boolean) => void
  toggleOpen: () => void
  selectedValue?: string
  setSelectedValue: (v: string) => void
  highlightedIndex: number
  setHighlightedIndex: (i: number) => void
  listReference: React.RefObject<HTMLUListElement | null>
  handleKeyDown: (event: KeyboardEvent) => void
}

export const useSelect = ({
  register,
  name,
  options = [],
  defaultValue,
  searchable = false,
}: UseSelectProperties): UseSelectReturn => {
  // Resolve register from prop or optional provider
  const provider = useOptionalFormContext() as FormMethods<FieldValues> | undefined
  const registerFunction: UseFormRegister<FieldValues> | undefined =
    register ?? provider?.register

  const registerProperties = useMemo<Partial<UseFormRegisterReturn>>(() => {
    if (typeof registerFunction === 'function' && name) {
      try {
        return registerFunction(name) as UseFormRegisterReturn
      } catch {
        return {}
      }
    }

    return {}
  }, [registerFunction, name])

  // normalize options
  const normalizedOptions = useMemo<SelectOption[]>(
    () => options.map((o) => (typeof o === 'string' ? { value: o, label: o } : o)),
    [options],
  )

  const [query, setQuery] = useState<string>('')
  const [isOpen, setIsOpen] = useState<boolean>(false)
  const [selectedValue, setSelectedValue] = useState<string | undefined>(defaultValue)
  const [highlightedIndex, setHighlightedIndex] = useState<number>(-1)

  const filtered = useMemo(() => {
    if (!searchable || !query) return normalizedOptions
    const q = query.toLowerCase()

    return normalizedOptions.filter(
      (o) =>
        String(o.label).toLowerCase().includes(q) || o.value.toLowerCase().includes(q),
    )
  }, [normalizedOptions, query, searchable])

  const toggleOpen = useCallback(() => setIsOpen((s) => !s), [])

  const handleSelect = useCallback((value: string) => {
    setSelectedValue(value)
    setIsOpen(false)
    setQuery('')
  }, [])

  const listReference = useRef<HTMLUListElement | null>(null)

  const handleKeyDown = useCallback(
    (event: KeyboardEvent) => {
      if (!isOpen) return

      if (event.key === 'ArrowDown') {
        event.preventDefault()
        setHighlightedIndex((i) => Math.min(i + 1, filtered.length - 1))
      } else if (event.key === 'ArrowUp') {
        event.preventDefault()
        setHighlightedIndex((i) => Math.max(i - 1, 0))
      } else if (event.key === 'Enter') {
        event.preventDefault()
        if (highlightedIndex >= 0 && highlightedIndex < filtered.length) {
          handleSelect(filtered[highlightedIndex].value)
        }
      } else if (event.key === 'Escape') {
        setIsOpen(false)
      }
    },
    [isOpen, filtered, highlightedIndex, handleSelect],
  )

  return {
    registerProperties,
    normalizedOptions,
    filteredOptions: filtered,
    query,
    setQuery,
    isOpen,
    setIsOpen,
    toggleOpen,
    selectedValue,
    setSelectedValue: handleSelect,
    highlightedIndex,
    setHighlightedIndex,
    listReference,
    handleKeyDown,
  }
}

export default useSelect
