import type { Meta as StoryMeta, StoryObj } from '@storybook/react-vite'
import type { ComponentType, JSX } from 'react'
import { expect, userEvent, within } from 'storybook/test'

import { AppStoreProvider } from '@/stores/useAppStore'

import { ModalManager, ModalProvider, useModal } from '../index'

const Meta = {
  title: 'Organisms/ModalManager',
  component: ModalManager,
  decorators: [
    (Story: ComponentType): JSX.Element => (
      <AppStoreProvider>
        <Story />
      </AppStoreProvider>
    )
  ],
  tags: ['autodocs']
} satisfies StoryMeta<typeof ModalManager>

export default Meta

type Story = StoryObj<typeof Meta>

/**
 * Default state: No modals are active.
 */
export const Default: Story = {}

/**
 * Demonstrates a custom modal being shown.
 */
export const WithCustomModal: Story = {
  render: (): JSX.Element => {
    const Example = (): JSX.Element => {
      const { show } = useModal()

      return (
        <div>
          <button
            type="button"
            onClick={() =>
              show(<div data-testid="custom-content">Custom Modal Content</div>)
            }
          >
            Open Custom Modal
          </button>
          <ModalManager />
        </div>
      )
    }

    return <Example />
  },
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement)
    const button = canvas.getByRole('button', { name: /open custom modal/i })
    await userEvent.click(button)

    // Modals are often in portals, so we search document.body
    const content = await within(document.body).findByTestId('custom-content')
    await expect(content).toBeInTheDocument()
    await expect(content).toHaveTextContent('Custom Modal Content')
  }
}

/**
 * Demonstrates a confirmation modal.
 */
export const WithConfirmModal: Story = {
  render: (): JSX.Element => {
    const Example = (): JSX.Element => {
      const { show } = useModal()
      const handleOpen = (): void => {
        show({
          type: 'confirm',
          props: {
            title: 'Confirm Action',
            message: 'Are you sure you want to proceed?',
            onConfirm: (): void => {
              console.log('Confirmed')
            },
            onCancel: (): void => {
              console.log('Cancelled')
            }
          }
        })
      }

      return (
        <div>
          <button type="button" onClick={handleOpen}>
            Open Confirm Modal
          </button>
          <ModalManager />
        </div>
      )
    }

    return <Example />
  },
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement)
    const button = canvas.getByRole('button', { name: /open confirm modal/i })

    // Count dialogs before opening
    const dialogsBefore = document.querySelectorAll('[role="dialog"]').length

    await userEvent.click(button)

    // Wait for the modal title to appear (unique to this modal)
    const title = await within(document.body).findByText(
      'Confirm Action',
      {},
      { timeout: 3000 }
    )

    // Get the dialog that contains this title
    const newDialog = title.closest('[role="dialog"]') as HTMLElement
    await expect(newDialog).toBeInTheDocument()

    // Verify that exactly one new dialog was added
    const allDialogs = document.querySelectorAll('[role="dialog"]')
    await expect(allDialogs.length).toBe(dialogsBefore + 1)

    // Verify the modal content
    await expect(
      within(newDialog).getByText('Are you sure you want to proceed?')
    ).toBeInTheDocument()

    // Verify buttons exist
    const confirmButton = within(newDialog).getByRole('button', { name: /ok/i })
    await expect(confirmButton).toBeInTheDocument()

    const cancelButton = within(newDialog).getByRole('button', { name: /cancel/i })
    await expect(cancelButton).toBeInTheDocument()
  }
}

/**
 * Demonstrates multiple modals stacked.
 */
export const MultipleModals: Story = {
  render: (): JSX.Element => {
    const Example = (): JSX.Element => {
      const { show } = useModal()
      const handleOpenMultiple = (): void => {
        show(<div data-testid="modal-1">First Modal</div>)
        show(<div data-testid="modal-2">Second Modal</div>)
      }

      return (
        <div>
          <button type="button" onClick={handleOpenMultiple}>
            Open Multiple Modals
          </button>
          <ModalManager />
        </div>
      )
    }

    return <Example />
  },
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement)
    const button = canvas.getByRole('button', { name: /open multiple modals/i })
    await userEvent.click(button)

    const modal1 = await within(document.body).findByTestId('modal-1')
    const modal2 = await within(document.body).findByTestId('modal-2')

    await expect(modal1).toBeInTheDocument()
    await expect(modal2).toBeInTheDocument()
  }
}

/**
 * Stories for ModalProvider
 */
export const ProviderDefault: StoryObj<typeof ModalProvider> = {
  render: (): JSX.Element => (
    <ModalProvider>
      <div style={{ padding: '20px', border: '1px solid #ccc' }}>
        <h3>App Content</h3>
        <p>This content is wrapped by ModalProvider.</p>
      </div>
    </ModalProvider>
  )
}

export const ProviderWithModal: StoryObj<typeof ModalProvider> = {
  render: (): JSX.Element => {
    const Example = (): JSX.Element => {
      const { show } = useModal()

      return (
        <ModalProvider>
          <button
            type="button"
            onClick={() => show(<div data-testid="provider-modal">Provider Modal</div>)}
          >
            Open Modal via Provider
          </button>
        </ModalProvider>
      )
    }

    return <Example />
  },
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement)
    const button = canvas.getByRole('button', { name: /open modal via provider/i })
    await userEvent.click(button)

    const modal = await within(document.body).findByTestId('provider-modal')
    await expect(modal).toBeInTheDocument()
  }
}

/**
 * Tests the fallback branch in ModalManager (lines 67-68).
 * Covers the case where desc.props fields have default fallbacks.
 */
export const ConfirmModalWithDefaults: Story = {
  render: (): JSX.Element => {
    const Example = (): JSX.Element => {
      const { show } = useModal()
      const handleOpen = (): void => {
        // Show confirm modal with minimal props to trigger default fallbacks
        show({
          type: 'confirm',
          props: {}
        })
      }

      return (
        <div>
          <button type="button" onClick={handleOpen} data-testid="open-defaults-button">
            Open Confirm with Defaults
          </button>
          <ModalManager />
        </div>
      )
    }

    return <Example />
  },
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement)
    const button = canvas.getByTestId('open-defaults-button')

    await userEvent.click(button)

    // Wait for the new modal to appear - it should have empty title
    // Use getAllByRole and find the one with empty title
    await new Promise((resolve) => setTimeout(resolve, 500))

    const dialogs = document.body.querySelectorAll('[role="dialog"]')
    const newDialog = Array.from(dialogs).find(
      (dialog) => dialog.querySelector('#confirm-modal-title')?.textContent === ''
    )

    await expect(newDialog).toBeTruthy()
  }
}
