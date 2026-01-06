import { useMemo, useState, useRef } from 'react'
import type {
  FieldValues,
  UseFormRegister,
  UseFormRegisterReturn
} from 'react-hook-form'

import type { FormMethods } from '@/components/organisms/Form'
import { useOptionalFormContext } from '@/components/organisms/Form'

export type SelectOption = {
  label: React.ReactNode
  value: string
  disabled?: boolean
  id?: string
}

type UseSelectProperties = {
  defaultValue?: string
  name?: string
  options?: Array<string | SelectOption>
  placeholder?: string
  register?: UseFormRegister<FieldValues>
  searchable?: boolean
}

export type UseSelectReturn = {
  filteredOptions: SelectOption[]
  highlightedIndex: number
  isOpen: boolean
  listReference: React.RefObject<HTMLUListElement | null>
  normalizedOptions: SelectOption[]
  query: string
  registerProperties: Partial<UseFormRegisterReturn>
  selectedLabel: React.ReactNode
  selectedNativeValue?: string
  selectedOption?: SelectOption
  selectedValue?: string
  setHighlightedIndex: (i: number) => void
  setIsOpen: (v: boolean) => void
  setQuery: (q: string) => void
  setSelectedValue: (v: string) => void
}

export const useSelect = ({
  defaultValue,
  name,
  options = [],
  placeholder,
  register,
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

        const opt = o as SelectOption
        const value = String(opt.value ?? '')

        return {
          value,
          label: opt.label,
          id: `${value}__${index}`,
          disabled: opt.disabled
        }
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

  // Resolve selected option (by internal id) and provide a display label and native value
  const selectedOption =
    typeof selectedValue === 'undefined'
      ? undefined
      : normalizedOptions.find((o) => o.id === selectedValue)

  const selectedLabel = selectedOption?.label ?? placeholder ?? ''
  const selectedNativeValue = selectedOption?.value

  // When integrated with react-hook-form, update the form value when selection changes.
  const setSelectedValue = (v: string): void => {
    // Accept either an internal `id` or an original `value`.
    // Resolve to the canonical option so we can store the unique `id` for UI
    // while writing the original `value` to the form provider.
    const incoming = v
    const resolvedOpt =
      normalizedOptions.find((o) => o.id === incoming) ||
      normalizedOptions.find((o) => o.value === incoming)

    const idToSet = resolvedOpt?.id ?? incoming
    const valueToWrite = resolvedOpt?.value ?? incoming

    // Instrumentation: log incoming value and resolved option details
    // to help debug why empty strings may be written into the form.

    // instrumentation removed
    setSelectedValueState(idToSet)

    if (typeof name === 'string') {
      if (valueToWrite === '') {
        // Avoid writing empty string values into the form provider which
        // can clear existing selections. Log and skip the write.
      } else if (provider?.setValue) {
        try {
          provider.setValue(name, valueToWrite)
        } catch {
          // ignore form setValue errors
        }
      } else if (registerProperties) {
        try {
          const onChangeCandidate = (
            registerProperties as Partial<UseFormRegisterReturn>
          ).onChange
          if (typeof onChangeCandidate === 'function') {
            onChangeCandidate({
              target: { name, value: valueToWrite }
            } as unknown as Event)
          }
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
    selectedOption,
    selectedLabel,
    selectedNativeValue,
    highlightedIndex,
    setHighlightedIndex,
    listReference
  }
}
