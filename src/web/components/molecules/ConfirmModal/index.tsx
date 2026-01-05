import type { JSX } from 'react'

import { Button } from '@/components/atoms/Button'
import { Heading } from '@/components/atoms/Heading'
import { Flex } from '@/components/molecules/Flex'
import { FlexColumn } from '@/components/molecules/FlexColumn'
import { Paragraph } from '@/components/molecules/Paragraph'
// ConfirmModal no longer renders its own Modal wrapper.
// The ModalProvider is responsible for rendering a Modal around
// any modal content provided via the `show` API.

import * as styles from './style.css'

type ConfirmModalProperties = {
  title: string
  message: string
  icon?: React.ReactNode
  onConfirm: () => void
  onCancel: () => void
  confirmText?: string
  cancelText?: string
}

// ConfirmModal now returns the inner content only.
// It is intended to be passed to the ModalProvider's `show` API,
// which will render the surrounding Modal.
export const ConfirmModal = ({
  title,
  message,
  icon,
  onConfirm,
  onCancel,
  confirmText = 'OK',
  cancelText = 'Cancel'
}: ConfirmModalProperties): JSX.Element => (
  <FlexColumn className={styles.container}>
    <Flex align="center" gap="s" className={styles.header}>
      {icon && <div className={styles.icon}>{icon}</div>}
      <Heading level={3} className={styles.title}>
        {title}
      </Heading>
    </Flex>
    <Paragraph className={styles.message}>{message}</Paragraph>
    <Flex justify="end" gap="s" className={styles.actions}>
      <Button type="button" onClick={onCancel} kind="secondary">
        {cancelText}
      </Button>
      <Button type="button" onClick={onConfirm} kind="primary">
        {confirmText}
      </Button>
    </Flex>
  </FlexColumn>
)
