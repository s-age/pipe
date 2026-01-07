import { clsx } from 'clsx'
import type { JSX } from 'react'
import { createPortal } from 'react-dom'

import { Button } from '@/components/atoms/Button'
import { Text } from '@/components/atoms/Text'
import { Box } from '@/components/molecules/Box'
import { Flex } from '@/components/molecules/Flex'
import { FlexColumn } from '@/components/molecules/FlexColumn'
import type { ToastItem } from '@/stores/useToastStore'

import { useToast } from './hooks/useToast'
import { useToastHandlers } from './hooks/useToastHandlers'
import { useToastItemHandlers } from './hooks/useToastItemHandlers'
import * as styles from './style.css'

type Position =
  | 'top-left'
  | 'top-center'
  | 'top-right'
  | 'bottom-left'
  | 'bottom-center'
  | 'bottom-right'

const allPositions: Position[] = [
  'top-left',
  'top-center',
  'top-right',
  'bottom-left',
  'bottom-center',
  'bottom-right'
]

const Icon = ({ status }: { status: ToastItem['status'] }): JSX.Element => {
  if (status === 'success') return <Text className={styles.icon}>✓</Text>
  if (status === 'failure') return <Text className={styles.icon}>✕</Text>

  return <Text className={styles.icon}>!</Text>
}

const statusClassMap: Record<ToastItem['status'], string> = {
  success: styles.statusSuccess,
  failure: styles.statusFailure,
  warning: styles.statusWarning
}

const ToastItem = ({
  item,
  removeToast
}: {
  item: ToastItem
  removeToast: (id: string) => void
}): JSX.Element => {
  const { exiting, handleClose, handleMouseEnter, handleMouseLeave } =
    useToastItemHandlers({ item, removeToast })

  return (
    <Box
      role={item.status === 'failure' ? 'alert' : 'status'}
      aria-live={item.status === 'failure' ? 'assertive' : 'polite'}
      className={clsx(
        styles.toast,
        exiting ? styles.exit : styles.enter,
        statusClassMap[item.status]
      )}
      onMouseEnter={handleMouseEnter}
      onMouseLeave={handleMouseLeave}
    >
      <Flex gap="s" align="start">
        <Icon status={item.status} />
        <FlexColumn className={styles.content}>
          {item.title ? <Text className={styles.title}>{item.title}</Text> : null}
          {item.description ? (
            <Text className={styles.description}>{item.description}</Text>
          ) : null}
        </FlexColumn>
        {item.dismissible ? (
          <Button
            kind="ghost"
            size="small"
            className={styles.close}
            onClick={handleClose}
            aria-label="Close"
          >
            ×
          </Button>
        ) : null}
      </Flex>
    </Box>
  )
}

export const Toasts = (): JSX.Element => {
  const { removeToast, toasts } = useToast()
  const { grouped } = useToastHandlers(toasts)

  return createPortal(
    allPositions.map((pos) => (
      <FlexColumn key={pos} className={styles.container} data-pos={pos} gap="s">
        {grouped[pos].map((item) => (
          <ToastItem key={item.id} item={item} removeToast={removeToast} />
        ))}
      </FlexColumn>
    )),
    document.body
  )
}
