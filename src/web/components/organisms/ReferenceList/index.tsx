import type { JSX } from 'react'

import { ErrorMessage } from '@/components/atoms/ErrorMessage'
import { Label } from '@/components/atoms/Label'
import { Accordion } from '@/components/molecules/Accordion'
import { MetaLabel, MetaItem } from '@/components/molecules/MetaItem'
import { Paragraph } from '@/components/molecules/Paragraph'
import { UnorderedList } from '@/components/molecules/UnorderedList'
import { FileSearchExplorer } from '@/components/organisms/FileSearchExplorer'
import { useOptionalFormContext } from '@/components/organisms/Form'
import type { SessionDetail } from '@/lib/api/session/getSession'

import { ReferenceComponent } from '../Reference'
import { useReferenceListHandlers } from './hooks/useReferenceListHandlers'
import { referenceSummary } from './style.css'
import { referencesList, noItemsMessage } from './style.css'

type ReferenceListProperties = {
  sessionDetail: SessionDetail
  placeholder?: string
  refreshSessions: () => Promise<void>
}

export const ReferenceList = ({
  sessionDetail,
  placeholder = 'Type to search files... (select from suggestions)',
  refreshSessions
}: ReferenceListProperties): JSX.Element => {
  const formContext = useOptionalFormContext()
  const errors = formContext?.formState?.errors?.references

  const {
    handleReferencesChange,
    references,
    existsValue,
    accordionOpen,
    setAccordionOpen
  } = useReferenceListHandlers(sessionDetail, formContext)

  return (
    <MetaItem>
      <Label>
        <MetaLabel>References:</MetaLabel>
      </Label>

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
        open={accordionOpen}
        onOpenChange={setAccordionOpen}
      >
        <UnorderedList className={referencesList}>
          {references.map((reference, index) => (
            <ReferenceComponent
              key={reference.path}
              reference={reference}
              currentSessionId={sessionDetail.sessionId || null}
              index={index}
              refreshSessions={refreshSessions}
            />
          ))}
        </UnorderedList>
        {references.length === 0 && (
          <Paragraph className={noItemsMessage}>No references added yet.</Paragraph>
        )}
        {errors && <ErrorMessage error={errors as never} />}
      </Accordion>
    </MetaItem>
  )
}
