import { useState, useCallback, useRef, useEffect, useMemo } from 'react'
import type { JSX, ChangeEvent, KeyboardEvent } from 'react'

import { useOptionalFormContext } from '@/components/organisms/Form'
import { getProcedures, type ProcedureOption } from '@/lib/api/procedures/getProcedures'

import {
  container,
  input,
  suggestionList,
  suggestionItem,
  selectedSuggestionItem,
  selectedProcedureContainer,
  selectedProcedureTag
} from './style.css'

type ProcedureSelectProperties = {
  placeholder?: string
}

export const ProcedureSelect = (properties: ProcedureSelectProperties): JSX.Element => {
  const { placeholder = 'Select procedure' } = properties

  const formContext = useOptionalFormContext()
  const watch = formContext?.watch
  const setValue = formContext?.setValue

  const selectedProcedure = watch?.('procedure') || null

  const [procedureOptions, setProcedureOptions] = useState<ProcedureOption[]>([])
  const [query, setQuery] = useState('')
  const [selectedIndex, setSelectedIndex] = useState(-1)
  const [isLoaded, setIsLoaded] = useState(false)
  const [showSuggestions, setShowSuggestions] = useState(false)
  const inputReference = useRef<HTMLInputElement>(null)
  const suggestionListReference = useRef<HTMLUListElement>(null)

  // Load procedures on mount
  useEffect(() => {
    const loadProcedures = async (): Promise<void> => {
      if (!isLoaded) {
        try {
          const procedures = await getProcedures()
          setProcedureOptions(procedures)
          setIsLoaded(true)
        } catch (error) {
          console.error('Failed to fetch procedures:', error)
        }
      }
    }
    void loadProcedures()
  }, [isLoaded])

  // Compute display query from selectedProcedure
  const displayQuery = useMemo(() => {
    if (selectedProcedure) {
      const procedure = procedureOptions.find((p) => p.value === selectedProcedure)

      return procedure ? procedure.label : ''
    }

    return query
  }, [selectedProcedure, procedureOptions, query])

  const handleInputChange = useCallback(
    (event: ChangeEvent<HTMLInputElement>) => {
      const value = event.target.value
      if (selectedProcedure) {
        // If editing while selected, clear selection
        setValue?.('procedure', null)
      }
      setQuery(value)
      setShowSuggestions(true)
    },
    [selectedProcedure, setValue]
  )

  const handleInputFocus = useCallback(() => {
    setShowSuggestions(true)
  }, [])

  const handleInputBlur = useCallback(() => {
    setTimeout(() => setShowSuggestions(false), 200)
  }, [])

  const handleProcedureSelect = useCallback(
    (procedure: ProcedureOption) => {
      setValue?.('procedure', procedure.value)
      setQuery('')
      setShowSuggestions(false)
      setSelectedIndex(-1)
    },
    [setValue]
  )

  const handleProcedureRemove = useCallback(() => {
    setValue?.('procedure', null)
    setQuery('')
  }, [setValue])

  const handleKeyDown = useCallback(
    (event: KeyboardEvent<HTMLInputElement>) => {
      if (!showSuggestions || procedureOptions.length === 0) return

      const filtered = procedureOptions.filter((procedure) =>
        procedure.label.toLowerCase().includes(query.toLowerCase())
      )

      switch (event.key) {
        case 'ArrowDown':
          event.preventDefault()
          setSelectedIndex((previous) =>
            previous < filtered.length - 1 ? previous + 1 : 0
          )
          break
        case 'ArrowUp':
          event.preventDefault()
          setSelectedIndex((previous) =>
            previous > 0 ? previous - 1 : filtered.length - 1
          )
          break
        case 'Enter':
          event.preventDefault()
          if (selectedIndex >= 0 && selectedIndex < filtered.length) {
            handleProcedureSelect(filtered[selectedIndex])
          }
          break
        case 'Escape':
          setShowSuggestions(false)
          setSelectedIndex(-1)
          inputReference.current?.blur()
          break
        default:
          console.log('Unhandled key:', event.key)
          break
      }
    },
    [showSuggestions, procedureOptions, query, selectedIndex, handleProcedureSelect]
  )

  // Scroll selected item into view when selectedIndex changes
  useEffect(() => {
    if (selectedIndex >= 0 && suggestionListReference.current) {
      const selectedElement = suggestionListReference.current.children[
        selectedIndex
      ] as HTMLElement
      if (selectedElement) {
        selectedElement.scrollIntoView({
          behavior: 'smooth',
          block: 'nearest'
        })
      }
    }
  }, [selectedIndex])

  const handleSuggestionClick = useCallback(
    (event: React.MouseEvent<HTMLLIElement>) => {
      const procedureValue = event.currentTarget.dataset.procedure
      const procedure = procedureOptions.find((p) => p.value === procedureValue)
      if (procedure) {
        handleProcedureSelect(procedure)
      }
    },
    [procedureOptions, handleProcedureSelect]
  )

  const filteredProcedures = procedureOptions.filter((procedure) =>
    procedure.label.toLowerCase().includes(query.toLowerCase())
  )

  return (
    <div className={container}>
      <div className={container}>
        <input
          ref={inputReference}
          type="text"
          value={displayQuery}
          onChange={handleInputChange}
          onFocus={handleInputFocus}
          onBlur={handleInputBlur}
          onKeyDown={handleKeyDown}
          placeholder={placeholder}
          className={input}
          autoComplete="off"
          {...formContext?.register('procedure')}
        />
        {showSuggestions && filteredProcedures.length > 0 && (
          <ul className={suggestionList} ref={suggestionListReference}>
            {filteredProcedures.map((procedure, index) => (
              <li
                key={procedure.value}
                className={
                  index === selectedIndex ? selectedSuggestionItem : suggestionItem
                }
                onClick={handleSuggestionClick}
                data-procedure={procedure.value}
              >
                {procedure.label}
              </li>
            ))}
          </ul>
        )}
      </div>
      {selectedProcedure && (
        <div className={selectedProcedureContainer}>
          <span className={selectedProcedureTag} onClick={handleProcedureRemove}>
            {procedureOptions.find((p) => p.value === selectedProcedure)?.label} ×
          </span>
        </div>
      )}
    </div>
  )
}
