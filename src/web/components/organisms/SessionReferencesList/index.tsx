import clsx from 'clsx'
import { JSX } from 'react'

import Button from '@/components/atoms/Button'
import Checkbox from '@/components/atoms/Checkbox'
import Label from '@/components/atoms/Label'
import { SessionDetail } from '@/lib/api/session/getSession'
import { Reference } from '@/types/reference'

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
  noItemsMessage,
} from './style.css'
import { useReferenceActions } from './useReferenceActions'
import { colors } from '../../../styles/colors.css'

type SessionReferencesListProps = {
  sessionDetail: SessionDetail | null
  currentSessionId: string | null
  setSessionDetail: (data: SessionDetail | null) => void
  setError: (error: string | null) => void
  refreshSessions: () => Promise<void>
}

export const SessionReferencesList = ({
  sessionDetail,
  currentSessionId,
  setSessionDetail,
  setError,
  refreshSessions,
}: SessionReferencesListProps): JSX.Element => {
  const {
    handleUpdateReferencePersist,
    handleUpdateReferenceTtl,
    handleUpdateReferenceDisabled,
  } = useReferenceActions(sessionDetail, setSessionDetail, setError, refreshSessions)

  const handleReferenceCheckboxChange = (index: number): void => {
    if (!currentSessionId || !sessionDetail) return
    const newReferences = [...sessionDetail.references]
    newReferences[index].disabled = !newReferences[index].disabled
    handleUpdateReferenceDisabled(
      currentSessionId,
      index,
      newReferences[index].disabled,
    )
  }

  const handleReferencePersistToggle = (index: number): void => {
    if (!currentSessionId || !sessionDetail) return
    const newReferences = [...sessionDetail.references]
    newReferences[index].persist = !newReferences[index].persist
    handleUpdateReferencePersist(currentSessionId, index, newReferences[index].persist)
  }

  const handleReferenceTtlChange = (
    index: number,
    action: 'increment' | 'decrement',
  ): void => {
    if (!currentSessionId || !sessionDetail) return
    const newReferences = [...sessionDetail.references]
    const currentTtl = newReferences[index].ttl !== null ? newReferences[index].ttl : 3
    const newTtl =
      action === 'increment'
        ? (currentTtl || 0) + 1
        : Math.max(0, (currentTtl || 0) - 1)
    newReferences[index].ttl = newTtl
    handleUpdateReferenceTtl(currentSessionId, index, newTtl)
  }

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
                  onChange={() => handleReferenceCheckboxChange(index)}
                  className={referenceCheckboxMargin}
                />
                <Button
                  kind="ghost"
                  size="xsmall"
                  style={{ minWidth: '32px' }}
                  onClick={() => handleReferencePersistToggle(index)}
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
                  style={{
                    textDecoration: reference.disabled ? 'line-through' : 'none',
                    color: reference.disabled ? colors.grayText : 'inherit',
                  }}
                >
                  {reference.path}
                </span>
              </Label>
              <div className={ttlControls}>
                <Button
                  kind="primary"
                  size="xsmall"
                  onClick={() => handleReferenceTtlChange(index, 'decrement')}
                >
                  -
                </Button>
                <span className={ttlValue}>
                  {reference.ttl !== null ? reference.ttl : 3}
                </span>
                <Button
                  kind="primary"
                  size="xsmall"
                  onClick={() => handleReferenceTtlChange(index, 'increment')}
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
