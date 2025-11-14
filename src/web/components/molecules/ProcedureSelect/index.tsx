import { useState, useCallback, useRef, useEffect } from 'react'
import type { JSX, KeyboardEvent } from 'react'

import { ErrorMessage } from '@/components/atoms/ErrorMessage'
import { useOptionalFormContext } from '@/components/organisms/Form'
import { getProcedures, type ProcedureOption } from '@/lib/api/procedures/getProcedures'

import {
  container,
  input,
  suggestionList,
  suggestionItem,
  selectedSuggestionItem
} from './style.css'

type ProcedureSelectProperties = {
  placeholder?: string
}

export const ProcedureSelect = (properties: ProcedureSelectProperties): JSX.Element => {
  const { placeholder = 'Select procedure' } = properties

  const formContext = useOptionalFormContext()
  const currentValue = formContext?.watch?.('procedure') || ''
  const error = formContext?.formState?.errors?.procedure

  const [procedureOptions, setProcedureOptions] = useState<ProcedureOption[]>([])
  const [selectedIndex, setSelectedIndex] = useState(-1)
  const [isLoaded, setIsLoaded] = useState(false)
  const [showSuggestions, setShowSuggestions] = useState(false)
  const inputReference = useRef<HTMLInputElement>(null)
  const suggestionListReference = useRef<HTMLUListElement>(null)
  const containerReference = useRef<HTMLDivElement>(null)

  const handleInputFocus = useCallback(() => {
    setShowSuggestions(true)

    // Load procedures on first focus
    if (!isLoaded) {
      const loadProcedures = async (): Promise<void> => {
        try {
          const procedures = await getProcedures()
          setProcedureOptions(procedures)
          setIsLoaded(true)
        } catch (error) {
          console.error('Failed to fetch procedures:', error)
        }
      }
      void loadProcedures()
    }
  }, [setShowSuggestions, isLoaded])

  const handleProcedureSelect = useCallback(
    (procedureValue: string) => {
      formContext?.setValue?.('procedure', procedureValue)
      setShowSuggestions(false)
      setSelectedIndex(-1)
      inputReference.current?.blur()
    },
    [formContext, setShowSuggestions, setSelectedIndex]
  )

  const filteredProcedures = procedureOptions.filter((procedure) =>
    procedure.value.toLowerCase().includes(currentValue.toLowerCase())
  )

  const handleKeyDown = useCallback(
    (event: KeyboardEvent<HTMLInputElement>) => {
      if (!showSuggestions || filteredProcedures.length === 0) return

      switch (event.key) {
        case 'ArrowDown':
          event.preventDefault()
          setSelectedIndex((previous) =>
            previous < filteredProcedures.length - 1 ? previous + 1 : 0
          )
          break
        case 'ArrowUp':
          event.preventDefault()
          setSelectedIndex((previous) =>
            previous > 0 ? previous - 1 : filteredProcedures.length - 1
          )
          break
        case 'Enter':
          event.preventDefault()
          if (selectedIndex >= 0 && selectedIndex < filteredProcedures.length) {
            handleProcedureSelect(filteredProcedures[selectedIndex].value)
          }
          break
        case 'Escape':
          setShowSuggestions(false)
          setSelectedIndex(-1)
          inputReference.current?.blur()
          break
        default:
          break
      }
    },
    [
      showSuggestions,
      filteredProcedures,
      selectedIndex,
      handleProcedureSelect,
      setSelectedIndex,
      setShowSuggestions
    ]
  )

  // Close suggestions when clicking outside
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent): void => {
      const target = event.target as Node

      // Check if click is outside the entire container
      if (containerReference.current && !containerReference.current.contains(target)) {
        setShowSuggestions(false)
        setSelectedIndex(-1)
      }
    }

    document.addEventListener('mousedown', handleClickOutside)

    return (): void => {
      document.removeEventListener('mousedown', handleClickOutside)
    }
  }, [])

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
      if (procedureValue) {
        handleProcedureSelect(procedureValue)
      }
    },
    [handleProcedureSelect]
  )

  return (
    <div className={container} ref={containerReference}>
      <input
        ref={inputReference}
        type="text"
        onFocus={handleInputFocus}
        onKeyDown={handleKeyDown}
        placeholder={placeholder}
        className={input}
        autoComplete="off"
        {...formContext?.register('procedure')}
      />
      {error && <ErrorMessage error={error as never} />}
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
  )
}
