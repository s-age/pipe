import { useState, useCallback, useRef, useEffect } from 'react'
import type { JSX, ChangeEvent, KeyboardEvent } from 'react'

import { getRoles, type RoleOption } from '@/lib/api/roles/getRoles'
import type { SessionDetail } from '@/lib/api/session/getSession'

import {
  container,
  input,
  suggestionList,
  suggestionItem,
  selectedSuggestionItem,
  selectedRolesContainer,
  selectedRoleTag
} from './style.css'

type RolesSelectProperties = {
  placeholder?: string
  sessionDetail: SessionDetail | null
  onChange?: (roles: string[]) => void
}

export const RolesSelect = (properties: RolesSelectProperties): JSX.Element => {
  const { placeholder = 'Select roles', sessionDetail, onChange } = properties
  console.log('sessionDetail.roles', sessionDetail?.roles ?? [])

  const [roleOptions, setRoleOptions] = useState<RoleOption[]>([])
  const [selectedRoles, setSelectedRoles] = useState<string[]>(
    sessionDetail?.roles ?? []
  )
  const [query, setQuery] = useState('')
  const [selectedIndex, setSelectedIndex] = useState(-1)
  const [isLoaded, setIsLoaded] = useState(false)
  const [showSuggestions, setShowSuggestions] = useState(false)
  const inputReference = useRef<HTMLInputElement>(null)
  const suggestionListReference = useRef<HTMLUListElement>(null)

  const handleInputChange = useCallback((event: ChangeEvent<HTMLInputElement>) => {
    setQuery(event.target.value)
    setShowSuggestions(true)
  }, [])

  const handleInputFocus = useCallback(() => {
    setShowSuggestions(true)

    // Load roles on first focus
    if (!isLoaded) {
      const loadRoles = async (): Promise<void> => {
        try {
          const roles = await getRoles()
          setRoleOptions(roles)
          setIsLoaded(true)
        } catch (error) {
          console.error('Failed to fetch roles:', error)
        }
      }
      void loadRoles()
    }
  }, [isLoaded])

  const handleInputBlur = useCallback(() => {
    setTimeout(() => setShowSuggestions(false), 200)
  }, [])

  const handleRoleSelect = useCallback(
    (role: RoleOption) => {
      if (!selectedRoles.includes(role.value)) {
        const newSelected = [...selectedRoles, role.value]
        setSelectedRoles(newSelected)
        onChange?.(newSelected)
      }
      setQuery('')
      setShowSuggestions(false)
      setSelectedIndex(-1)
    },
    [selectedRoles, onChange]
  )

  const handleRoleRemove = useCallback(
    (roleValue: string) => {
      const newSelected = selectedRoles.filter((r) => r !== roleValue)
      setSelectedRoles(newSelected)
      onChange?.(newSelected)
    },
    [selectedRoles, onChange]
  )

  const handleKeyDown = useCallback(
    (event: KeyboardEvent<HTMLInputElement>) => {
      if (!showSuggestions || roleOptions.length === 0) return

      const filtered = roleOptions.filter(
        (role) =>
          role.label.toLowerCase().includes(query.toLowerCase()) &&
          !selectedRoles.includes(role.value)
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
            handleRoleSelect(filtered[selectedIndex])
          }
          break
        case 'Escape':
          setShowSuggestions(false)
          setSelectedIndex(-1)
          inputReference.current?.blur()
          break
      }
    },
    [
      showSuggestions,
      roleOptions,
      query,
      selectedIndex,
      selectedRoles,
      handleRoleSelect
    ]
  )

  // Close suggestions when clicking outside
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent): void => {
      if (
        inputReference.current &&
        suggestionListReference.current &&
        !inputReference.current.contains(event.target as Node) &&
        !suggestionListReference.current.contains(event.target as Node)
      ) {
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
      const roleValue = event.currentTarget.dataset.role
      const role = roleOptions.find((r) => r.value === roleValue)
      if (role) {
        handleRoleSelect(role)
      }
    },
    [roleOptions, handleRoleSelect]
  )

  const handleTagClick = useCallback(
    (event: React.MouseEvent<HTMLSpanElement>) => {
      const roleValue = event.currentTarget.dataset.role
      if (roleValue) {
        handleRoleRemove(roleValue)
      }
    },
    [handleRoleRemove]
  )

  const filteredRoles = roleOptions.filter(
    (role) =>
      role.label.toLowerCase().includes(query.toLowerCase()) &&
      !selectedRoles.includes(role.value)
  )

  return (
    <div className={container}>
      <div className={container}>
        <input
          ref={inputReference}
          type="text"
          value={query}
          onChange={handleInputChange}
          onFocus={handleInputFocus}
          onBlur={handleInputBlur}
          onKeyDown={handleKeyDown}
          placeholder={placeholder}
          className={input}
          autoComplete="off"
        />
        {showSuggestions && filteredRoles.length > 0 && (
          <ul className={suggestionList} ref={suggestionListReference}>
            {filteredRoles.map((role, index) => (
              <li
                key={role.value}
                className={
                  index === selectedIndex ? selectedSuggestionItem : suggestionItem
                }
                onClick={handleSuggestionClick}
                data-role={role.value}
              >
                {role.label}
              </li>
            ))}
          </ul>
        )}
      </div>
      <div className={selectedRolesContainer}>
        {selectedRoles.map((roleValue) => {
          const role = roleOptions.find((r) => r.value === roleValue)
          // Display the role even if roleOptions hasn't loaded yet
          const displayLabel = role?.label ?? roleValue

          return (
            <span
              key={roleValue}
              className={selectedRoleTag}
              onClick={handleTagClick}
              data-role={roleValue}
            >
              {displayLabel} ×
            </span>
          )
        })}
      </div>
    </div>
  )
}
