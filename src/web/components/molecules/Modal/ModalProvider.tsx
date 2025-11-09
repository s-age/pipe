import type { JSX } from 'react'
import React from 'react'

import { Modal } from './index'

type ModalEntry = {
  id: number
  content: React.ReactNode
}

type ModalContextValue = {
  show: (content: React.ReactNode) => number
  hide: (id?: number) => void
}

const ModalContext = React.createContext<ModalContextValue | null>(null)

export const ModalProvider = ({
  children,
}: {
  children: React.ReactNode
}): JSX.Element => {
  const [stack, setStack] = React.useState<ModalEntry[]>([])

  const idSeedReference = React.useRef(1)
  const handlersReference = React.useRef<Record<number, () => void>>({})

  const show = React.useCallback((content: React.ReactNode): number => {
    const id = idSeedReference.current++
    setStack((s) => [...s, { id, content }])

    // create a stable close handler for this id stored in a ref
    handlersReference.current[id] = (): void => {
      setStack((s) => s.filter((entryItem) => entryItem.id !== id))
    }

    return id
  }, [])

  const hide = React.useCallback((id?: number): void => {
    if (id == null) {
      setStack((s) => s.slice(0, -1))

      return
    }

    setStack((s) => s.filter((entryItem) => entryItem.id !== id))
  }, [])

  const value = React.useMemo(() => ({ show, hide }), [show, hide])

  const ModalItem = ({ entry }: { entry: ModalEntry }): JSX.Element => {
    const handler = handlersReference.current[entry.id]

    return (
      <Modal key={entry.id} open={true} onClose={handler}>
        {entry.content}
      </Modal>
    )
  }

  return (
    <ModalContext.Provider value={value}>
      {children}

      {/* render modal stack */}
      {stack.map((entry) => (
        <ModalItem key={entry.id} entry={entry} />
      ))}
    </ModalContext.Provider>
  )
}

export const useModalContext = (): ModalContextValue => {
  const context = React.useContext(ModalContext)
  if (!context) throw new Error('useModalContext must be used within ModalProvider')

  return context
}
