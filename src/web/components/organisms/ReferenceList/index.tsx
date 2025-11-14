import type { JSX } from 'react'
import { useMemo } from 'react'
import { useWatch } from 'react-hook-form'

import { ErrorMessage } from '@/components/atoms/ErrorMessage'
import { Label } from '@/components/atoms/Label'
import { SuggestionItem } from '@/components/organisms/FileSearchExplorer/SuggestionItem'
import { useOptionalFormContext } from '@/components/organisms/Form'
import type { Reference } from '@/types/reference'

import { ReferenceComponent } from '../Reference'
import { useReferenceListHandlers } from './hooks/useReferenceListHandlers'
import { useReferenceListSuggest } from './hooks/useReferenceListSuggest'
import {
  metaItem,
  metaItemLabel,
  referencesList,
  noItemsMessage,
  addReferenceContainer,
  addReferenceInput,
  suggestionList
} from './style.css'

type ReferenceListProperties = {
  placeholder?: string
  currentSessionId: string | null
}

export const ReferenceList = ({
  placeholder = 'Type to search files... (select from suggestions)',
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
  const { actions } = useReferenceListHandlers(formContext, references)
  const {
    inputValue,
    suggestions,
    selectedIndex,
    inputReference,
    suggestionListReference,
    handleFocus,
    handleInputChange,
    handleKeyDown,
    handleSuggestionClick
  } = useReferenceListSuggest(actions, references)

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
