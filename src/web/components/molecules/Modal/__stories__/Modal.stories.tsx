import type { Meta as StoryMeta, StoryObj } from '@storybook/react-vite'
import type { JSX } from 'react'
import { useState } from 'react'
import { expect, fn, userEvent, within } from 'storybook/test'

import { Modal } from '../index'

const Meta = {
  title: 'Molecules/Modal',
  component: Modal,
  tags: ['autodocs'],
  args: {
    onClose: fn()
  }
} satisfies StoryMeta<typeof Modal>

export default Meta
type Story = StoryObj<typeof Meta>

export const Default: Story = {
  args: {
    isOpen: true,
    children: (
      <div style={{ padding: '20px', background: 'white', borderRadius: '8px' }}>
        <h2 id="modal-title">Modal Title</h2>
        <p id="modal-description">This is the modal content.</p>
        <button type="button">Close Button</button>
      </div>
    ),
    'aria-labelledby': 'modal-title',
    'aria-describedby': 'modal-description'
  },
  play: async ({ canvasElement }) => {
    const body = canvasElement.ownerDocument.body
    const modal = await within(body).findByRole('dialog')
    await expect(modal).toBeInTheDocument()
    await expect(modal).toHaveAttribute('aria-modal', 'true')
    await expect(modal).toHaveAttribute('aria-labelledby', 'modal-title')
    await expect(modal).toHaveAttribute('aria-describedby', 'modal-description')
    await expect(within(modal).getByText('Modal Title')).toBeInTheDocument()
  }
}

export const Closed: Story = {
  args: {
    isOpen: false,
    children: <div>This should not be visible</div>
  },
  play: async ({ canvasElement }) => {
    const body = canvasElement.ownerDocument.body
    const modal = within(body).queryByRole('dialog')
    await expect(modal).not.toBeInTheDocument()
  }
}

export const Controlled: Story = {
  args: {
    isOpen: false
  },
  render: (arguments_): JSX.Element => {
    const ControlledModal = (): JSX.Element => {
      const [isOpen, setIsOpen] = useState(false)

      const handleClose = (): void => {
        setIsOpen(false)
        arguments_.onClose?.()
      }

      return (
        <div>
          <button type="button" onClick={() => setIsOpen(true)}>
            Open Modal
          </button>
          <Modal
            {...arguments_}
            isOpen={isOpen}
            onClose={handleClose}
          >
            <div style={{ padding: '20px', background: 'white', borderRadius: '8px' }}>
              <h2>Controlled Modal</h2>
              <p>Click the close button to dismiss.</p>
              <button type="button" onClick={handleClose}>
                Close
              </button>
            </div>
          </Modal>
        </div>
      )
    }

    return <ControlledModal />
  },
  play: async ({ args, canvasElement }) => {
    const canvas = within(canvasElement)
    const openButton = canvas.getByRole('button', { name: /open modal/i })
    await userEvent.click(openButton)

    const body = canvasElement.ownerDocument.body
    const modal = await within(body).findByRole('dialog')
    await expect(modal).toBeInTheDocument()

    const closeButton = within(modal).getByRole('button', { name: /close/i })
    await userEvent.click(closeButton)

    // Wait for modal to be removed
    await expect(within(body).queryByRole('dialog')).not.toBeInTheDocument()
    await expect(args.onClose).toHaveBeenCalled()
  }
}
