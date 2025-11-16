import { useMemo, useState, useRef, useEffect } from 'react'
import type {
  FieldValues,
  UseFormRegister,
  UseFormRegisterReturn,
  UseFormSetValue
} from 'react-hook-form'

import type { FormMethods } from '@/components/organisms/Form'
import { useOptionalFormContext } from '@/components/organisms/Form'

export type SelectOption = { value: string; label: React.ReactNode }

type UseMultipleSelectProperties = {
  register?: UseFormRegister<FieldValues>
  name?: string
  options?: Array<string | SelectOption>
  defaultValue?: string[]
  searchable?: boolean
}

export type UseMultipleSelectReturn = {
  registerProperties: Partial<UseFormRegisterReturn>
  normalizedOptions: SelectOption[]
  filteredOptions: SelectOption[]
  query: string
  setQuery: (q: string) => void
  isOpen: boolean
  setIsOpen: (v: boolean) => void
  selectedValues: string[]
  setSelectedValues: (v: string[]) => void
  highlightedIndex: number
  setHighlightedIndex: (i: number) => void
  listReference: React.RefObject<HTMLUListElement | null>
}

export const useMultipleSelect = ({
  name,
  options = [],
  defaultValue = [],
  searchable = false
}: UseMultipleSelectProperties): UseMultipleSelectReturn => {
  // Resolve register from prop or optional provider
  const provider = useOptionalFormContext() as FormMethods<FieldValues> | undefined
  const registerFunction: UseFormRegister<FieldValues> | undefined = provider?.register
  const setValueFunction: UseFormSetValue<FieldValues> | undefined = provider?.setValue

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
    [options]
  )

  const [query, setQuery] = useState<string>('')
  const [isOpen, setIsOpen] = useState<boolean>(false)
  const [selectedValues, setSelectedValues] = useState<string[]>(defaultValue)
  const [highlightedIndex, setHighlightedIndex] = useState<number>(-1)

  // Sync selectedValues with form
  useEffect(() => {
    if (setValueFunction && name) {
      setValueFunction(name, selectedValues)
    }
  }, [selectedValues, setValueFunction, name])

  const filteredOptions = useMemo(() => {
    if (!searchable || !query) return normalizedOptions
    const q = query.toLowerCase()

    return normalizedOptions.filter(
      (o) =>
        String(o.label).toLowerCase().includes(q) || o.value.toLowerCase().includes(q)
    )
  }, [normalizedOptions, query, searchable])

  const listReference = useRef<HTMLUListElement | null>(null)

  return {
    registerProperties,
    normalizedOptions,
    filteredOptions,
    query,
    setQuery,
    isOpen,
    setIsOpen,
    selectedValues,
    setSelectedValues,
    highlightedIndex,
    setHighlightedIndex,
    listReference
  }
}
