import clsx from 'clsx'
import type { JSX } from 'react'

import { Button } from '@/components/atoms/Button'
import { Checkbox } from '@/components/atoms/Checkbox'
import { Label } from '@/components/atoms/Label'
import type { SessionDetail } from '@/lib/api/session/getSession'
import type { Reference } from '@/types/reference'

import { useSessionReferencesHandlers } from './hooks/useSessionReferencesHandlers'
import { useSessionReferencesListHandlers } from './hooks/useSessionReferencesListHandlers'
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
  referenceCheckboxMargin,
  lockIconStyle,
  persistButton,
  noItemsMessage
} from './style.css'

type SessionReferencesListProperties = {
  sessionDetail: SessionDetail | null
  currentSessionId: string | null
  setSessionDetail: (data: SessionDetail | null) => void
  refreshSessions: () => Promise<void>
}

export const SessionReferencesList = ({
  sessionDetail,
  currentSessionId,
  setSessionDetail,
  refreshSessions
}: SessionReferencesListProperties): JSX.Element => {
  const {
    handleReferenceCheckboxChange,
    handleReferencePersistToggle,
    handleReferenceTtlChange
  } = useSessionReferencesListHandlers({
    sessionDetail,
    currentSessionId,
    setSessionDetail,
    refreshSessions
  })

  const { handleCheckboxChange, handlePersistToggle, handleTtlAction } =
    useSessionReferencesHandlers({
      handleReferenceCheckboxChange,
      handleReferencePersistToggle,
      handleReferenceTtlChange
    })

  if (!sessionDetail || sessionDetail.references.length === 0) {
    return (
      <div className={metaItem}>
        <Label className={metaItemLabel}>References:</Label>
        <p className={noItemsMessage}>No references for this session.</p>
      </div>
    )
  }

  return (
    <div className={metaItem}>
      <Label className={metaItemLabel}>References:</Label>
      <ul className={referencesList}>
        {sessionDetail.references.map((reference: Reference, index: number) => (
          <li key={index} className={referenceItem}>
            <div className={referenceControls}>
              <Label className={referenceLabel}>
                <Checkbox
                  checked={!reference.disabled}
                  onChange={handleCheckboxChange}
                  data-index={String(index)}
                  className={referenceCheckboxMargin}
                />
                <Button
                  kind="ghost"
                  size="xsmall"
                  className={persistButton}
                  onClick={handlePersistToggle}
                  data-index={String(index)}
                >
                  <span
                    className={clsx(materialIcons, lockIconStyle)}
                    data-locked={reference.persist}
                  >
                    {reference.persist ? 'lock' : 'lock_open'}
                  </span>
                </Button>
                <span
                  data-testid="reference-path"
                  className={referencePath}
                  data-disabled={String(Boolean(reference.disabled))}
                >
                  {reference.path}
                </span>
              </Label>
              <div className={ttlControls}>
                <Button
                  kind="primary"
                  size="xsmall"
                  onClick={handleTtlAction}
                  data-index={String(index)}
                  data-action="decrement"
                >
                  -
                </Button>
                <span className={ttlValue}>
                  {reference.ttl !== null ? reference.ttl : 3}
                </span>
                <Button
                  kind="primary"
                  size="xsmall"
                  onClick={handleTtlAction}
                  data-index={String(index)}
                  data-action="increment"
                >
                  +
                </Button>
              </div>
            </div>
          </li>
        ))}
      </ul>
    </div>
  )
}
