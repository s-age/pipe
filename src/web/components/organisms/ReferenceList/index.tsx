import clsx from 'clsx'
import type { JSX } from 'react'
import { useCallback, useState } from 'react'

import { Button } from '@/components/atoms/Button'
import { Label } from '@/components/atoms/Label'
import { ToggleSwitch } from '@/components/molecules/ToggleSwitch'
import { Tooltip } from '@/components/molecules/Tooltip'
import { useFileSearchExplorerActions } from '@/components/organisms/FileSearchExplorer/hooks/useFileSearchExplorerActions'
import { SuggestionItem } from '@/components/organisms/FileSearchExplorer/SuggestionItem'
import type { SessionDetail } from '@/lib/api/session/getSession'
import type { Reference } from '@/types/reference'

import { useReferenceControls } from './hooks/useReferenceHandlers'
import {
  metaItem,
  metaItemLabel,
  referencesList,
  referenceItem,
  referenceControls,
  referenceLabel,
  referencePath,
  materialIcons,
  ttlControls,
  ttlValue,
  lockIconStyle,
  persistButton,
  noItemsMessage,
  addReferenceContainer,
  addReferenceInput,
  addReferenceButton,
  suggestionList
} from './style.css'

type ReferenceListProperties = {
  sessionDetail: SessionDetail | null
  currentSessionId: string | null
  setSessionDetail: (data: SessionDetail | null) => void
  refreshSessions: () => Promise<void>
}

const ReferenceToggle = ({
  index,
  reference,
  onToggle
}: {
  index: number
  reference: Reference
  onToggle: (index: number) => void
}): JSX.Element => {
  const handleChange = useCallback(() => {
    onToggle(index)
  }, [onToggle, index])

  return (
    <Tooltip content="Toggle reference enabled">
      <ToggleSwitch
        checked={!reference.disabled}
        onChange={handleChange}
        ariaLabel={`Toggle reference ${reference.path} enabled`}
      />
    </Tooltip>
  )
}

export const ReferenceList = ({
  sessionDetail,
  currentSessionId,
  setSessionDetail: _setSessionDetail,
  refreshSessions
}: ReferenceListProperties): JSX.Element => {
  const { handlePersistToggle, handleTtlAction, toggleDisabled, handleAddReference } =
    useReferenceControls({ sessionDetail, currentSessionId, refreshSessions })
  const actions = useFileSearchExplorerActions()
  const [inputValue, setInputValue] = useState('')
  const [suggestions, setSuggestions] = useState<
    { name: string; isDirectory: boolean }[]
  >([])
  const [rootSuggestions, setRootSuggestions] = useState<
    { name: string; isDirectory: boolean }[]
  >([])
  const [selectedIndex, setSelectedIndex] = useState<number>(-1)

  const loadRootSuggestions = useCallback(async () => {
    if (rootSuggestions.length === 0) {
      const lsResult = await actions.getLsData({ final_path_list: [] })
      if (lsResult) {
        const rootEntries = lsResult.entries.map((entry) => ({
          name: entry.name,
          isDirectory: entry.is_dir
        }))
        setRootSuggestions(rootEntries)
      }
    }
  }, [actions, rootSuggestions.length])

  const handleFocus = useCallback(() => {
    void loadRootSuggestions()
  }, [loadRootSuggestions])

  const handleInputChange = useCallback(
    async (event: React.ChangeEvent<HTMLInputElement>) => {
      const value = event.target.value
      setInputValue(value)
      setSelectedIndex(-1)
      if (value.includes('/')) {
        const parts = value.split('/')
        const pathParts = parts.slice(0, -1).filter((p) => p)
        const prefix = parts[parts.length - 1] || ''
        if (pathParts.length > 0) {
          const lsResult = await actions.getLsData({ final_path_list: pathParts })
          if (lsResult) {
            const filtered = lsResult.entries
              .filter((entry) => entry.name.startsWith(prefix))
              .map((entry) => ({
                name: entry.name,
                isDirectory: entry.is_dir
              }))
            setSuggestions(filtered)
          }
        } else {
          const filtered = rootSuggestions.filter((item) =>
            item.name.startsWith(prefix)
          )
          setSuggestions(filtered)
        }
      } else if (value.length > 0) {
        const filtered = rootSuggestions.filter((item) => item.name.startsWith(value))
        setSuggestions(filtered)
      } else {
        setSuggestions([])
      }
    },
    [actions, rootSuggestions]
  )

  const loadSubDirectorySuggestions = useCallback(
    async (pathParts: string[]) => {
      const lsResult = await actions.getLsData({ final_path_list: pathParts })
      if (lsResult) {
        const entries = lsResult.entries.map((entry) => ({
          name: entry.name,
          isDirectory: entry.is_dir
        }))
        setSuggestions(entries)
      }
    },
    [actions]
  )

  const handleKeyDown = useCallback(
    (event: React.KeyboardEvent<HTMLInputElement>) => {
      if (suggestions.length === 0) return
      if (event.key === 'ArrowDown') {
        event.preventDefault()
        setSelectedIndex((previous) => (previous + 1) % suggestions.length)
      } else if (event.key === 'ArrowUp') {
        event.preventDefault()
        setSelectedIndex(
          (previous) => (previous - 1 + suggestions.length) % suggestions.length
        )
      } else if (event.key === 'Enter') {
        event.preventDefault()
        if (selectedIndex >= 0) {
          const selected = suggestions[selectedIndex]
          if (selected.isDirectory) {
            const newPath = `${inputValue.split('/').slice(0, -1).join('/')}/${selected.name}/`
            setInputValue(newPath)
            // Load suggestions for the new directory
            const pathParts = newPath.split('/').filter((p) => p)
            void loadSubDirectorySuggestions(pathParts)
          } else {
            setInputValue(selected.name)
          }
          setSelectedIndex(-1)
        }
      }
    },
    [suggestions, selectedIndex, inputValue, loadSubDirectorySuggestions]
  )

  const handleSuggestionClick = useCallback(
    async (suggestion: string | { name: string; isDirectory: boolean }) => {
      if (typeof suggestion === 'string') {
        setInputValue(suggestion)
      } else {
        if (suggestion.isDirectory) {
          const newPath = `${inputValue.split('/').slice(0, -1).join('/')}/${suggestion.name}/`
          setInputValue(newPath)
          // Load suggestions for the new directory
          const pathParts = newPath.split('/').filter((p) => p)
          await loadSubDirectorySuggestions(pathParts)
        } else {
          setInputValue(suggestion.name)
        }
      }
      setSelectedIndex(-1)
    },
    [inputValue, loadSubDirectorySuggestions]
  )

  const handleAdd = useCallback(async () => {
    if (inputValue.trim()) {
      await handleAddReference(inputValue.trim())
      setInputValue('')
      setSuggestions([])
      setSelectedIndex(-1)
    }
  }, [inputValue, handleAddReference])

  if (!sessionDetail || sessionDetail.references.length === 0) {
    return (
      <div className={metaItem}>
        <Label className={metaItemLabel}>References:</Label>
        <div className={addReferenceContainer}>
          <input
            type="text"
            value={inputValue}
            onChange={handleInputChange}
            onFocus={handleFocus}
            onKeyDown={handleKeyDown}
            placeholder="Enter reference path..."
            className={addReferenceInput}
          />
          <button onClick={handleAdd} className={addReferenceButton}>
            Add
          </button>
          {suggestions.length > 0 && (
            <ul className={suggestionList}>
              {suggestions.map((suggestion, index) => (
                <SuggestionItem
                  key={index}
                  suggestion={suggestion}
                  onClick={handleSuggestionClick}
                  isSelected={index === selectedIndex}
                />
              ))}
            </ul>
          )}
        </div>
        <p className={noItemsMessage}>No references yet. Add one to get started!</p>
      </div>
    )
  }

  return (
    <div className={metaItem}>
      <Label className={metaItemLabel}>References:</Label>
      <div className={addReferenceContainer}>
        <input
          type="text"
          value={inputValue}
          onChange={handleInputChange}
          onFocus={handleFocus}
          onKeyDown={handleKeyDown}
          placeholder="Enter reference path..."
          className={addReferenceInput}
        />
        <button onClick={handleAdd} className={addReferenceButton}>
          Add
        </button>
        {suggestions.length > 0 && (
          <ul className={suggestionList}>
            {suggestions.map((suggestion, index) => (
              <SuggestionItem
                key={index}
                suggestion={suggestion}
                onClick={handleSuggestionClick}
                isSelected={index === selectedIndex}
              />
            ))}
          </ul>
        )}
      </div>
      <ul className={referencesList}>
        {sessionDetail.references.map((reference: Reference, index: number) => (
          <li key={index} className={referenceItem}>
            <div className={referenceControls}>
              <div className={referenceLabel}>
                <Tooltip
                  content={reference.persist ? 'Unlock reference' : 'Lock reference'}
                >
                  <Button
                    kind="ghost"
                    size="xsmall"
                    className={persistButton}
                    onClick={handlePersistToggle}
                    data-index={String(index)}
                    aria-label={
                      reference.persist
                        ? `Unlock reference ${reference.path}`
                        : `Lock reference ${reference.path}`
                    }
                  >
                    <span
                      className={clsx(materialIcons, lockIconStyle)}
                      data-locked={reference.persist}
                    >
                      {reference.persist ? 'lock' : 'lock_open'}
                    </span>
                  </Button>
                </Tooltip>
                <span
                  data-testid="reference-path"
                  className={referencePath}
                  data-disabled={String(Boolean(reference.disabled))}
                >
                  {reference.path}
                </span>
              </div>
              <div className={ttlControls}>
                <Tooltip content="Decrease TTL">
                  <Button
                    kind="primary"
                    size="xsmall"
                    onClick={handleTtlAction}
                    data-index={String(index)}
                    data-action="decrement"
                    aria-label={`Decrease TTL for ${reference.path}`}
                  >
                    -
                  </Button>
                </Tooltip>
                <span className={ttlValue}>
                  {reference.ttl !== null ? reference.ttl : 3}
                </span>
                <Tooltip content="Increase TTL">
                  <Button
                    kind="primary"
                    size="xsmall"
                    onClick={handleTtlAction}
                    data-index={String(index)}
                    data-action="increment"
                    aria-label={`Increase TTL for ${reference.path}`}
                  >
                    +
                  </Button>
                </Tooltip>
              </div>
              <ReferenceToggle
                index={index}
                reference={reference}
                onToggle={toggleDisabled}
              />
            </div>
          </li>
        ))}
      </ul>
    </div>
  )
}
