import { useMemo, type JSX } from 'react'

import { ErrorMessage } from '@/components/atoms/ErrorMessage'
import { Label } from '@/components/atoms/Label'
import { Accordion } from '@/components/molecules/Accordion'
import { FileSearchExplorer } from '@/components/organisms/FileSearchExplorer'
import { useOptionalFormContext } from '@/components/organisms/Form'
import type { SessionDetail } from '@/lib/api/session/getSession'
import { referenceSummary } from '@/styles/reference.css'

import { ReferenceComponent } from '../Reference'
import { useReferenceListHandlers } from './hooks/useReferenceListHandlers'
import { metaItem, metaItemLabel, referencesList, noItemsMessage } from './style.css'

type ReferenceListProperties = {
  sessionDetail: SessionDetail
  placeholder?: string
}

export const ReferenceList = ({
  sessionDetail,
  placeholder = 'Type to search files... (select from suggestions)'
}: ReferenceListProperties): JSX.Element => {
  const formContext = useOptionalFormContext()
  const errors = formContext?.formState?.errors?.references

  const { handleReferencesChange, references } = useReferenceListHandlers(
    sessionDetail,
    formContext
  )
  const existsValue = useMemo(
    () => references.map((reference) => reference.path),
    [references]
  )

  return (
    <div className={metaItem}>
      <Label className={metaItemLabel}>References:</Label>

      {/* Always-visible search / chips area */}
      <FileSearchExplorer
        existsValue={existsValue}
        placeholder={placeholder}
        onChange={handleReferencesChange}
      />

      {/* Collapsible list of reference items only */}
      <Accordion
        title={<span />}
        summary={
          <span
            className={referenceSummary}
          >{`${references.length} ${references.length === 1 ? 'reference' : 'references'} · Advanced settings`}</span>
        }
        defaultOpen={false}
      >
        <ul className={referencesList}>
          {references.map((reference, index) => (
            <ReferenceComponent
              key={index}
              reference={reference}
              currentSessionId={sessionDetail.session_id || null}
              index={index}
            />
          ))}
        </ul>
        {references.length === 0 && (
          <p className={noItemsMessage}>No references added yet.</p>
        )}
        {errors && <ErrorMessage error={errors as never} />}
      </Accordion>
    </div>
  )
}
