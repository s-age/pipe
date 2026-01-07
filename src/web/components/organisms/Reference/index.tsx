import clsx from 'clsx'
import type { JSX } from 'react'

import { Button } from '@/components/atoms/Button'
import { Text } from '@/components/atoms/Text'
import { Flex } from '@/components/molecules/Flex'
import { ListItem } from '@/components/molecules/ListItem'
import { ToggleSwitch } from '@/components/molecules/ToggleSwitch'
import { Tooltip } from '@/components/organisms/Tooltip'
import type { Reference } from '@/types/reference'

import { useReferenceHandlers } from './hooks/useReferenceHandlers'
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
  currentSessionId: string | null
  index: number
  reference: Reference
  refreshSessions: () => Promise<void>
}

export const ReferenceComponent = ({
  currentSessionId,
  index,
  reference,
  refreshSessions
}: ReferenceProperties): JSX.Element => {
  const { handlePersistToggle, handleToggle, handleTtlAction, localReference } =
    useReferenceHandlers(currentSessionId, reference, index, refreshSessions)

  const ttl = localReference.ttl !== null ? localReference.ttl : 3

  return (
    <ListItem className={referenceItem}>
      <Flex className={referenceLabel} align="center">
        <Tooltip
          content={localReference.persist ? 'Unlock reference' : 'Lock reference'}
          placement="bottom"
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
            <Text
              className={clsx(materialIcons, lockIconStyle)}
              data-locked={localReference.persist}
            >
              {localReference.persist ? 'lock' : 'lock_open'}
            </Text>
          </Button>
        </Tooltip>
        <Text
          data-testid="reference-path"
          className={referencePath}
          data-disabled={String(Boolean(localReference.disabled))}
        >
          {localReference.path}
        </Text>
      </Flex>

      <Flex className={referenceActions} align="center" justify="between">
        <Flex className={ttlControls} align="center" gap="s">
          <Tooltip content="Decrease TTL" placement="bottom">
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
          <Text className={ttlValue}>{ttl}</Text>
          <Tooltip content="Increase TTL" placement="bottom">
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
        </Flex>
        <Tooltip content="Toggle reference enabled" placement="bottom">
          <ToggleSwitch
            checked={!localReference.disabled}
            onChange={handleToggle}
            ariaLabel={`Toggle reference ${localReference.path} enabled`}
          />
        </Tooltip>
      </Flex>
    </ListItem>
  )
}
