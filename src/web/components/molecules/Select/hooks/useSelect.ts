import { useMemo, useState, useRef } from 'react'
import type {
  FieldValues,
  UseFormRegister,
  UseFormRegisterReturn
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
  selectedValue?: string
  setSelectedValue: (v: string) => void
  highlightedIndex: number
  setHighlightedIndex: (i: number) => void
  listReference: React.RefObject<HTMLUListElement | null>
}

export const useSelect = ({
  register,
  name,
  options = [],
  defaultValue,
  searchable = false
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
    [options]
  )

  const [query, setQuery] = useState<string>('')
  const [isOpen, setIsOpen] = useState<boolean>(false)
  const [selectedValue, setSelectedValue] = useState<string | undefined>(defaultValue)
  const [highlightedIndex, setHighlightedIndex] = useState<number>(-1)

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
    selectedValue,
    setSelectedValue,
    highlightedIndex,
    setHighlightedIndex,
    listReference
  }
}
