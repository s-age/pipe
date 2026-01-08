import React from 'react'
import type { JSX } from 'react'

import { ConfirmModal } from '@/components/molecules/ConfirmModal'
import { Modal } from '@/components/molecules/Modal'
import type { ModalEntry, ConfirmDescriptor } from '@/stores/useModalStore'

import { useModalManagerHandlers } from './hooks/useModalManagerHandlers'

export { useModal } from './hooks/useModal'

/**
 * ModalProvider - Context Provider
 *
 * Wraps application with ModalManager to enable modal functionality.
 *
 * @example
 * <ModalProvider>
 *   <App />
 * </ModalProvider>
 */
export const ModalProvider = ({
  children
}: {
  children: React.ReactNode
}): JSX.Element => (
  <>
    {children}
    <ModalManager />
  </>
)

/**
 * ModalItem - Internal Component
 *
 * Renders a single Modal entry from the stack.
 * Pure View component - no hooks, only props.
 */
const ModalItem = ({
  entry,
  isConfirmDescriptor,
  onClose
}: {
  entry: ModalEntry
  isConfirmDescriptor: (v: unknown) => v is ConfirmDescriptor
  onClose: () => void
}): JSX.Element | null => {
  const content = entry.content

  let innerJSX: React.ReactNode | null = null
  let ariaLabelledby: string | undefined
  let ariaDescribedby: string | undefined

  if (isConfirmDescriptor(content)) {
    const desc = content as {
      props: {
        message?: string
        title?: string
        onCancel?: () => void
        onConfirm?: () => void | Promise<void>
      }
    }
    innerJSX = (
      <ConfirmModal
        title={desc.props.title ?? ''}
        message={desc.props.message ?? ''}
        onConfirm={desc.props.onConfirm ?? ((): void => undefined)}
        onCancel={desc.props.onCancel ?? ((): void => undefined)}
      />
    )
    ariaLabelledby = 'confirm-modal-title'
    ariaDescribedby = 'confirm-modal-description'
  } else if (content != null && !isConfirmDescriptor(content)) {
    innerJSX = content as React.ReactNode
  }

  if (innerJSX == null) return null

  return (
    <Modal
      key={String(entry.id)}
      isOpen={true}
      onClose={onClose}
      aria-labelledby={ariaLabelledby}
      aria-describedby={ariaDescribedby}
    >
      {innerJSX}
    </Modal>
  )
}

/**
 * ModalManager - Organism Component
 *
 * Subscribes to Modal Store and renders list of Modal molecules.
 * Injects onClose handler to each Modal.
 *
 * Pattern: Organism (Store connection & List Rendering)
 */
export const ModalManager = (): JSX.Element | null => {
  const { createCloseHandler, isConfirmDescriptor, stack } = useModalManagerHandlers()

  if (typeof document === 'undefined') return null

  return (
    <>
      {stack.map((entry) => (
        <ModalItem
          key={String(entry.id)}
          entry={entry}
          onClose={createCloseHandler(entry.id)}
          isConfirmDescriptor={isConfirmDescriptor}
        />
      ))}
    </>
  )
}
