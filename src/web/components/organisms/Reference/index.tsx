import clsx from 'clsx'
import type { JSX } from 'react'

import { Button } from '@/components/atoms/Button'
import { ToggleSwitch } from '@/components/molecules/ToggleSwitch'
import { Tooltip } from '@/components/organisms/Tooltip'
import type { Reference } from '@/types/reference'

import { useReferenceHandlers } from './hooks/useReferenceHandlers'
import { useReferenceLifecycle } from './hooks/useReferenceLifecycle'
import {
  referenceItem,
  referenceLabel,
  referencePath,
  materialIcons,
  ttlControls,
  ttlValue,
  lockIconStyle,
  persistButton,
  referenceActions
} from './style.css'

type ReferenceProperties = {
  reference: Reference
  index: number
  currentSessionId: string | null
}

export const ReferenceComponent = ({
  reference,
  index,
  currentSessionId
}: ReferenceProperties): JSX.Element => {
  const { localReference, setLocalReference } = useReferenceLifecycle(reference)

  const { handlePersistToggle, handleTtlAction, handleToggle } = useReferenceHandlers(
    currentSessionId,
    localReference,
    index,
    setLocalReference
  )

  const ttl = localReference.ttl !== null ? localReference.ttl : 3

  return (
    <li className={referenceItem}>
      <div className={referenceLabel}>
        <Tooltip
          content={localReference.persist ? 'Unlock reference' : 'Lock reference'}
        >
          <Button
            kind="ghost"
            size="xsmall"
            className={persistButton}
            onClick={handlePersistToggle}
            data-index={String(index)}
            aria-label={
              localReference.persist
                ? `Unlock reference ${localReference.path}`
                : `Lock reference ${localReference.path}`
            }
          >
            <span
              className={clsx(materialIcons, lockIconStyle)}
              data-locked={localReference.persist}
            >
              {localReference.persist ? 'lock' : 'lock_open'}
            </span>
          </Button>
        </Tooltip>
        <span
          data-testid="reference-path"
          className={referencePath}
          data-disabled={String(Boolean(localReference.disabled))}
        >
          {localReference.path}
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
              aria-label={`Decrease TTL for ${localReference.path}`}
            >
              -
            </Button>
          </Tooltip>
          <span className={ttlValue}>{ttl}</span>
          <Tooltip content="Increase TTL">
            <Button
              kind="primary"
              size="xsmall"
              onClick={handleTtlAction}
              data-index={String(index)}
              data-action="increment"
              aria-label={`Increase TTL for ${localReference.path}`}
            >
              +
            </Button>
          </Tooltip>
        </div>
        <Tooltip content="Toggle reference enabled">
          <ToggleSwitch
            checked={!localReference.disabled}
            onChange={handleToggle}
            ariaLabel={`Toggle reference ${localReference.path} enabled`}
          />
        </Tooltip>
      </div>
    </li>
  )
}
