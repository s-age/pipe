import type { Meta as StoryMeta, StoryObj } from '@storybook/react-vite'
import type { JSX } from 'react'
import React from 'react'

import { Button } from '@/components/atoms/Button'
import { useModal } from '@/components/molecules/Modal/hooks/useModal'
import { ModalProvider } from '@/components/molecules/Modal/ModalProvider'

const Meta = {
  title: 'Atoms/Modal',
  tags: ['autodocs'],
} satisfies StoryMeta<unknown>

export default Meta
type Story = StoryObj<typeof Meta>

const Demo = (): JSX.Element => {
  const { show, hide } = useModal()

  const open = React.useCallback((): void => {
    const id = show(
      <div style={{ padding: 16 }}>
        <h3>Modal (Storybook)</h3>
        <p>This modal was opened from a Storybook story via useModal().</p>
        <div style={{ marginTop: 12 }}>
          <Button type="button" onClick={() => hide(id)}>
            Close
          </Button>
        </div>
      </div>,
    )
  }, [show, hide])

  return (
    <div style={{ padding: 12 }}>
      <Button type="button" onClick={open}>
        Open modal
      </Button>
    </div>
  )
}

export const Default: Story = {
  render: (): JSX.Element => (
    <ModalProvider>
      <Demo />
    </ModalProvider>
  ),
}
