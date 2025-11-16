import { useMemo, useState, useRef, useEffect } from 'react'
import type {
  FieldValues,
  UseFormRegister,
  UseFormRegisterReturn,
  UseFormSetValue
} from 'react-hook-form'

import type { FormMethods } from '@/components/organisms/Form'
import { useOptionalFormContext } from '@/components/organisms/Form'

export type SelectOption = {
  value: string
  label: React.ReactNode
  __origValue?: string
}

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
  const normalizedOptions = useMemo<SelectOption[]>(() => {
    // Filter out falsy entries and coerce into SelectOption shape safely
    const list = options
      .filter((o) => o !== null && o !== undefined)
      .map((o, index) => {
        let rawValue: string
        let label: React.ReactNode
        if (typeof o === 'string') {
          rawValue = o
          label = o
        } else {
          rawValue = typeof o.value === 'string' ? o.value : String(o.value ?? '')
          label = o.label ?? String(o.value ?? '')
        }

        // If the source value is empty, generate a stable placeholder
        // so each option has a unique value for selection tracking.
        const value = rawValue !== '' ? rawValue : `__empty_${index}`

        return {
          value,
          label,
          __origValue: rawValue
        }
      })

    return list
  }, [options])

  // Map normalized value -> original raw value (may be empty string)
  const valueToOrig = useMemo(() => {
    const m = new Map<string, string>()
    for (const o of normalizedOptions) {
      m.set(o.value, o.__origValue ?? o.value)
    }

    return m
  }, [normalizedOptions])

  // Map original/raw value -> array of normalized/internal values
  // (handles cases where multiple options share the same original value, e.g. empty strings)
  const origToValues = useMemo(() => {
    const m = new Map<string, string[]>()
    for (const o of normalizedOptions) {
      const key = o.__origValue ?? o.value
      const values = m.get(key) ?? []
      values.push(o.value)
      m.set(key, values)
    }

    return m
  }, [normalizedOptions])

  const [query, setQuery] = useState<string>('')
  const [isOpen, setIsOpen] = useState<boolean>(false)
  // Initialize selectedValues to the normalized/internal values that correspond
  // to any provided defaultValue (which are original/raw values coming from form data)
  const [selectedValues, setSelectedValues] = useState<string[]>(() =>
    defaultValue.flatMap((v) => origToValues.get(v) ?? [v])
  )
  const [highlightedIndex, setHighlightedIndex] = useState<number>(-1)

  // Sync selectedValues with form
  useEffect(() => {
    if (setValueFunction && name) {
      // Map placeholder values back to original values for form integration
      const toSet = selectedValues.map((v) => valueToOrig.get(v) ?? v)
      // Deduplicate values before setting into form
      setValueFunction(name, Array.from(new Set(toSet)))
    }
  }, [selectedValues, setValueFunction, name, valueToOrig])

  const filteredOptions = useMemo(() => {
    if (!searchable || !query) return normalizedOptions
    const q = String(query ?? '').toLowerCase()

    return normalizedOptions.filter((o) => {
      const label = String(o.label ?? '').toLowerCase()
      const value = String(o.value ?? '').toLowerCase()

      return label.includes(q) || value.includes(q)
    })
  }, [normalizedOptions, query, searchable])

  const listReference = useRef<HTMLUListElement | null>(null)

  // Debugging: log option counts to help diagnose missing options
  useEffect(() => {
    console.log(
      '[useMultipleSelect] normalizedOptions',
      normalizedOptions.length,
      normalizedOptions
    )
  }, [normalizedOptions])

  useEffect(() => {
    console.log(
      '[useMultipleSelect] filteredOptions',
      filteredOptions?.length ?? 0,
      filteredOptions
    )
  }, [filteredOptions])

  useEffect(() => {
    console.log('[useMultipleSelect] selectedValues', selectedValues)
  }, [selectedValues])

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
