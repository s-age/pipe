import type { JSX } from 'react'
import { useCallback, useMemo } from 'react'
import { useWatch } from 'react-hook-form'

import { ErrorMessage } from '@/components/atoms/ErrorMessage'
import { Label } from '@/components/atoms/Label'
import { useFileSearchExplorerActions } from '@/components/organisms/FileSearchExplorer/hooks/useFileSearchExplorerActions'
import { SuggestionItem } from '@/components/organisms/FileSearchExplorer/SuggestionItem'
import { useOptionalFormContext } from '@/components/organisms/Form'
import type { Reference } from '@/types/reference'

import { ReferenceComponent } from '../Reference'
import { useReferenceListHandlers } from './hooks/useReferenceListHandlers'
import {
  metaItem,
  metaItemLabel,
  referencesList,
  noItemsMessage,
  addReferenceContainer,
  addReferenceInput,
  addReferenceButton,
  suggestionList
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
  const watchedReferences = useWatch({
    control: formContext?.control,
    name: 'references'
  })
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
            <ReferenceComponent
              key={index}
              reference={reference}
              index={index}
              currentSessionId={currentSessionId}
              formContext={formContext}
            />
          ))}
        </ul>
      )}
    </div>
  )
}
