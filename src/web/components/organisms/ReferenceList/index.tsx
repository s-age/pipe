import clsx from 'clsx'
import type { JSX } from 'react'
import { useCallback } from 'react'

import { Button } from '@/components/atoms/Button'
import { Label } from '@/components/atoms/Label'
import { ToggleSwitch } from '@/components/molecules/ToggleSwitch'
import { Tooltip } from '@/components/molecules/Tooltip'
import { SuggestionItem } from '@/components/organisms/FileSearchExplorer/SuggestionItem'
import type { SessionDetail } from '@/lib/api/session/getSession'
import type { Reference } from '@/types/reference'

import { useReferenceControls } from './hooks/useReferenceHandlers'
import { useReferenceListActions } from './hooks/useReferenceListActions'
import { useReferenceListHandlers } from './hooks/useReferenceListHandlers'
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
  suggestionList,
  referenceActions
} from './style.css'

type ReferenceListProperties = {
  sessionDetail: SessionDetail | null
  currentSessionId: string | null
  setSessionDetail: (data: SessionDetail | null) => void
  refreshSessions?: () => Promise<void>
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
  const { handlePersistToggle, handleTtlAction, toggleDisabled } = useReferenceControls(
    { sessionDetail, currentSessionId, refreshSessions }
  )

  const actions = useReferenceListActions(
    sessionDetail,
    currentSessionId,
    refreshSessions
  )
  const {
    inputValue,
    suggestions,
    selectedIndex,
    inputReference,
    suggestionListReference,
    handleFocus,
    handleInputChange,
    handleKeyDown,
    handleSuggestionClick,
    handleAdd
  } = useReferenceListHandlers(actions)

  // Use sessionDetail references for display
  const currentReferences = sessionDetail?.references || []

  if (!sessionDetail || currentReferences.length === 0) {
    return (
      <div className={metaItem}>
        <Label className={metaItemLabel}>References:</Label>
        <div className={addReferenceContainer}>
          <input
            ref={inputReference}
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
            <ul ref={suggestionListReference} className={suggestionList}>
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
          ref={inputReference}
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
          <ul ref={suggestionListReference} className={suggestionList}>
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
        {currentReferences.map((reference: Reference, index: number) => (
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
              <div className={referenceActions}>
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
            </div>
          </li>
        ))}
      </ul>
    </div>
  )
}
