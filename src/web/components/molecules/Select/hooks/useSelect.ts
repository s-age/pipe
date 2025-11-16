import { useMemo, useState, useRef } from 'react'
import type {
  FieldValues,
  UseFormRegister,
  UseFormRegisterReturn
} from 'react-hook-form'

import type { FormMethods } from '@/components/organisms/Form'
import { useOptionalFormContext } from '@/components/organisms/Form'

export type SelectOption = { value: string; label: React.ReactNode; id?: string }

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

  // normalize options: ensure `value` is always a string to avoid runtime errors
  const normalizedOptions = useMemo<SelectOption[]>(
    () =>
      options.map((o, index) => {
        if (typeof o === 'string')
          return { value: String(o), label: o, id: `${String(o)}__${index}` }

        const value = String((o as any).value ?? '')

        return { value: value, label: (o as any).label, id: `${value}__${index}` }
      }),
    [options]
  )

  const [query, setQuery] = useState<string>('')
  const [isOpen, setIsOpen] = useState<boolean>(false)
  const [selectedValue, setSelectedValueState] = useState<string | undefined>(
    defaultValue
  )
  const [highlightedIndex, setHighlightedIndex] = useState<number>(-1)

  const filteredOptions = useMemo(() => {
    if (!searchable || !query) return normalizedOptions
    const q = String(query).toLowerCase()

    return normalizedOptions.filter((o) => {
      const labelString = String(o.label ?? '').toLowerCase()
      const valueString = String(o.value ?? '').toLowerCase()

      return labelString.includes(q) || valueString.includes(q)
    })
  }, [normalizedOptions, query, searchable])

  const listReference = useRef<HTMLUListElement | null>(null)

  // When integrated with react-hook-form, update the form value when selection changes.
  const setSelectedValue = (v: string) => {
    // Accept either an internal `id` or an original `value`.
    // Resolve to the canonical option so we can store the unique `id` for UI
    // while writing the original `value` to the form provider.
    const incoming = v
    const resolvedOpt =
      normalizedOptions.find((o) => o.id === incoming) ||
      normalizedOptions.find((o) => o.value === incoming)

    const idToSet = resolvedOpt?.id ?? incoming
    const valueToWrite = resolvedOpt?.value ?? incoming

    setSelectedValueState(idToSet)

    if (typeof name === 'string') {
      if (provider?.setValue) {
        try {
          provider.setValue(name, valueToWrite)
        } catch {
          // ignore form setValue errors
        }
      } else if (
        registerProperties &&
        typeof (registerProperties as any).onChange === 'function'
      ) {
        try {
          const onChange = (registerProperties as Partial<UseFormRegisterReturn>)
            .onChange!
          onChange({ target: { name, value: valueToWrite } } as unknown as Event)
        } catch {
          // ignore
        }
      }
    }
  }

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
