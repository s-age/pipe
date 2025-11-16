import type { JSX } from 'react'
import { useMemo } from 'react'
import { useWatch } from 'react-hook-form'

import { ErrorMessage } from '@/components/atoms/ErrorMessage'
import { Label } from '@/components/atoms/Label'
import { FileSearchExplorer } from '@/components/organisms/FileSearchExplorer'
import { useOptionalFormContext } from '@/components/organisms/Form'
import type { Reference } from '@/types/reference'

import { ReferenceComponent } from '../Reference'
import { useReferenceListHandlers } from './hooks/useReferenceListHandlers'
import { metaItem, metaItemLabel, referencesList, noItemsMessage } from './style.css'

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

  const { handleReferencesChange } = useReferenceListHandlers(formContext, references)

  const errors = formContext?.formState?.errors?.references

  const existsValue = references.map((reference) => reference.path)

  return (
    <div className={metaItem}>
      <Label className={metaItemLabel}>References:</Label>
      <FileSearchExplorer
        existsValue={existsValue}
        placeholder={placeholder}
        onChange={handleReferencesChange}
      />
      <ul className={referencesList}>
        {references.map((reference, index) => (
          <ReferenceComponent
            key={index}
            reference={reference}
            currentSessionId={currentSessionId}
            index={index}
          />
        ))}
      </ul>
      {references.length === 0 && (
        <p className={noItemsMessage}>No references added yet.</p>
      )}
      {errors && <ErrorMessage error={errors as never} />}
    </div>
  )
}
