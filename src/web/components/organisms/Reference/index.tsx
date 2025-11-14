import clsx from 'clsx'
import type { JSX } from 'react'
import { useCallback, useEffect, useMemo, useRef, useState } from 'react'
import type { UseFormReturn } from 'react-hook-form'

import { Button } from '@/components/atoms/Button'
import { ToggleSwitch } from '@/components/molecules/ToggleSwitch'
import { Tooltip } from '@/components/molecules/Tooltip'
import type { Reference } from '@/types/reference'

import { useReferenceHandlers } from './hooks/useReferenceHandlers'
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
  currentSessionId: string | null
  formContext?: UseFormReturn
}

export const ReferenceComponent = ({
  reference,
  index,
  currentSessionId,
  formContext
}: ReferenceProperties): JSX.Element => {
  const [localReference, setLocalReference] = useState(reference)

  // Update local state when prop changes
  useEffect(() => {
    setLocalReference(reference)
  }, [reference])

  const { handlePersistToggle, handleToggleDisabled, handleTtlAction } =
    useReferenceHandlers(
      currentSessionId,
      localReference,
      index,
      formContext,
      setLocalReference
    )
  const timeoutReference = useRef<NodeJS.Timeout | null>(null)

  const debouncedOnToggle = useMemo(
    (): (() => void) => () => {
      if (timeoutReference.current) {
        clearTimeout(timeoutReference.current)
      }
      timeoutReference.current = setTimeout(() => handleToggleDisabled(), 100)
    },
    [handleToggleDisabled]
  )

  const handleChange = useCallback(() => {
    debouncedOnToggle()
  }, [debouncedOnToggle])

  return (
    <li className={referenceItem}>
      <div className={referenceControls}>
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
            <span className={ttlValue}>
              {localReference.ttl !== null ? localReference.ttl : 3}
            </span>
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
              onChange={handleChange}
              ariaLabel={`Toggle reference ${localReference.path} enabled`}
            />
          </Tooltip>
        </div>
      </div>
    </li>
  )
}
