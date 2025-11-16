import type { JSX } from 'react'
import React, { useCallback, useEffect, useState } from 'react'
import { createPortal } from 'react-dom'

import { Modal } from '@/components/molecules/Modal'
import type { ModalEventData } from '@/lib/modalEvents'
import { onModalShow, onModalHide } from '@/lib/modalEvents'

type ModalEntry = {
  id: string
  content: React.ReactNode
}

const genId = (() => {
  let c = 0

  return (): string => `modal-${Date.now()}-${++c}`
})()

export const ModalManager = (): JSX.Element | null => {
  const [stack, setStack] = useState<ModalEntry[]>([])

  const handleShow = useCallback((data: ModalEventData): void => {
    const id = data.id ? String(data.id) : genId()
    const entry: ModalEntry = { id, content: data.content ?? null }
    setStack((s) => [...s, entry])
  }, [])

  const handleHide = useCallback((data: { id?: string | number }): void => {
    if (!data || data.id == null) {
      setStack((s) => s.slice(0, -1))

      return
    }
    const id = String(data.id)
    setStack((s) => s.filter((entryItem) => entryItem.id !== id))
  }, [])

  useEffect((): (() => void) => {
    const offShow = onModalShow(handleShow)
    const offHide = onModalHide(handleHide)

    return (): void => {
      offShow()
      offHide()
    }
  }, [handleShow, handleHide])

  const removeById = useCallback((id: string): void => {
    setStack((s) => s.filter((entryItem) => entryItem.id !== id))
  }, [])

  const ModalItem = ({ entry }: { entry: ModalEntry }): JSX.Element => {
    const handleClose = useCallback(() => removeById(entry.id), [entry.id])

    return (
      <Modal key={entry.id} open={true} onClose={handleClose}>
        {entry.content}
      </Modal>
    )
  }

  return createPortal(
    <>
      {stack.map((entry) => (
        <ModalItem key={entry.id} entry={entry} />
      ))}
    </>,
    document.body
  )
}
