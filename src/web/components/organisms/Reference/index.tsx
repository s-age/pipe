import clsx from 'clsx'
import type { JSX } from 'react'

import { Button } from '@/components/atoms/Button'
import { Tooltip } from '@/components/molecules/Tooltip'
import type { Reference } from '@/types/reference'

import { ReferenceToggle } from '../ReferenceList/ReferenceToggle'
import {
  referenceItem,
  referenceControls,
  referenceLabel,
  referencePath,
  materialIcons,
  ttlControls,
  ttlValue,
  lockIconStyle,
  persistButton,
  referenceActions
} from '../ReferenceList/style.css'

type ReferenceProperties = {
  reference: Reference
  index: number
  onPersistToggle: (event: React.MouseEvent<HTMLButtonElement>) => void
  onTtlAction: (event: React.MouseEvent<HTMLButtonElement>) => void
  onToggleDisabled: (index: number) => void
}

export const ReferenceComponent = ({
  reference,
  index,
  onPersistToggle,
  onTtlAction,
  onToggleDisabled
}: ReferenceProperties): JSX.Element => (
  <li className={referenceItem}>
    <div className={referenceControls}>
      <div className={referenceLabel}>
        <Tooltip content={reference.persist ? 'Unlock reference' : 'Lock reference'}>
          <Button
            kind="ghost"
            size="xsmall"
            className={persistButton}
            onClick={onPersistToggle}
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
              onClick={onTtlAction}
              data-index={String(index)}
              data-action="decrement"
              aria-label={`Decrease TTL for ${reference.path}`}
            >
              -
            </Button>
          </Tooltip>
          <span className={ttlValue}>{reference.ttl !== null ? reference.ttl : 3}</span>
          <Tooltip content="Increase TTL">
            <Button
              kind="primary"
              size="xsmall"
              onClick={onTtlAction}
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
          onToggle={onToggleDisabled}
        />
      </div>
    </div>
  </li>
)
