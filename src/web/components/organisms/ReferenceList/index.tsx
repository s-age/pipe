import clsx from 'clsx'
import type { JSX } from 'react'
import { useCallback, useMemo } from 'react'

import { Button } from '@/components/atoms/Button'
import { ErrorMessage } from '@/components/atoms/ErrorMessage'
import { Label } from '@/components/atoms/Label'
import { Tooltip } from '@/components/molecules/Tooltip'
import { useFileSearchExplorerActions } from '@/components/organisms/FileSearchExplorer/hooks/useFileSearchExplorerActions'
import { SuggestionItem } from '@/components/organisms/FileSearchExplorer/SuggestionItem'
import { useOptionalFormContext } from '@/components/organisms/Form'
import { editReferencePersist } from '@/lib/api/session/editReferencePersist'
import { editReferences } from '@/lib/api/session/editReferences'
import { editReferenceTtl } from '@/lib/api/session/editReferenceTtl'
import { emitToast } from '@/lib/toastEvents'
import type { Reference } from '@/types/reference'

import { useReferenceListHandlers } from './hooks/useReferenceListHandlers'
import { ReferenceToggle } from './ReferenceToggle'
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
  placeholder?: string
  currentSessionId: string | null
}

export const ReferenceList = ({
  placeholder = 'Enter reference path...',
  currentSessionId
}: ReferenceListProperties): JSX.Element => {
  const formContext = useOptionalFormContext()
  const watchedReferences = formContext?.watch?.('references')
  const references = useMemo(
    () => (watchedReferences || []) as Reference[],
    [watchedReferences]
  )

  const errors = formContext?.formState?.errors?.references
  const addReference = useCallback(
    async (path: string): Promise<void> => {
      const newReference: Reference = {
        path,
        ttl: 3,
        persist: false,
        disabled: false
      }
      formContext?.setValue?.('references', [...references, newReference])
    },
    [formContext, references]
  )
  const fileActions = useFileSearchExplorerActions()
  const actions = useMemo(
    () => ({
      loadRootSuggestions: async (): Promise<
        { name: string; isDirectory: boolean }[]
      > => {
        const lsResult = await fileActions.getLsData({ final_path_list: [] })
        if (lsResult) {
          return lsResult.entries.map((entry) => ({
            name: entry.name,
            isDirectory: entry.is_dir
          }))
        }

        return []
      },
      loadSubDirectorySuggestions: async (
        pathParts: string[]
      ): Promise<{ name: string; isDirectory: boolean }[]> => {
        const lsResult = await fileActions.getLsData({ final_path_list: pathParts })
        if (lsResult) {
          return lsResult.entries.map((entry) => ({
            name: entry.name,
            isDirectory: entry.is_dir
          }))
        }

        return []
      },
      addReference
    }),
    [addReference, fileActions]
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

  const handlePersistToggle = useCallback(
    async (event: React.MouseEvent<HTMLButtonElement>) => {
      if (!currentSessionId) return
      const index = Number(event.currentTarget.dataset.index)
      const newPersist = !references[index].persist
      try {
        await editReferencePersist(currentSessionId, index, newPersist)
        const updatedReferences = [...references]
        updatedReferences[index] = {
          ...updatedReferences[index],
          persist: newPersist
        }
        formContext?.setValue?.('references', updatedReferences, {
          shouldDirty: true
        })

        emitToast.success(
          `Reference ${newPersist ? 'locked' : 'unlocked'}: ${references[index].path}`
        )
      } catch (error) {
        console.error('Failed to update persist:', error)
        emitToast.failure('Failed to update reference lock state')
      }
    },
    [references, formContext, currentSessionId]
  )

  const handleTtlAction = useCallback(
    async (event: React.MouseEvent<HTMLButtonElement>) => {
      if (!currentSessionId) return
      const index = Number(event.currentTarget.dataset.index)
      const action = event.currentTarget.dataset.action
      const currentTtl = references[index].ttl ?? 3
      let newTtl = currentTtl
      if (action === 'increment') {
        newTtl = currentTtl + 1
      } else if (action === 'decrement' && currentTtl > 0) {
        newTtl = currentTtl - 1
      } else {
        return
      }

      try {
        await editReferenceTtl(currentSessionId, index, newTtl)
        const updatedReferences = [...references]
        updatedReferences[index] = {
          ...updatedReferences[index],
          ttl: newTtl
        }
        formContext?.setValue?.('references', updatedReferences, {
          shouldDirty: true
        })

        emitToast.success(`TTL updated to ${newTtl}: ${references[index].path}`)
      } catch (error) {
        console.error('Failed to update TTL:', error)
        emitToast.failure('Failed to update TTL')
      }
    },
    [references, formContext, currentSessionId]
  )

  const toggleDisabled = useCallback(
    async (index: number) => {
      if (!currentSessionId) return
      const updatedReferences = [...references]
      updatedReferences[index] = {
        ...updatedReferences[index],
        disabled: !updatedReferences[index].disabled
      }
      try {
        await editReferences(currentSessionId, updatedReferences)
        formContext?.setValue?.('references', updatedReferences)
      } catch (error) {
        console.error('Failed to toggle disabled:', error)
      }
    },
    [references, formContext, currentSessionId]
  )

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
          placeholder={placeholder}
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
      {errors && <ErrorMessage error={errors as never} />}
      {references.length === 0 ? (
        <p className={noItemsMessage}>No references yet. Add one to get started!</p>
      ) : (
        <ul className={referencesList}>
          {references.map((reference: Reference, index: number) => (
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
      )}
    </div>
  )
}
