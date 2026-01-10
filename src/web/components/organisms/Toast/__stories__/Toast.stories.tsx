import type { Meta as StoryMeta, StoryObj } from '@storybook/react-vite'
import { useEffect } from 'react'
import type { JSX } from 'react'
import { expect, userEvent, within } from 'storybook/test'

import { Button } from '@/components/atoms/Button'
import { Flex } from '@/components/molecules/Flex'

import { useToast } from '../hooks/useToast'
import { Toasts } from '../index'

const Meta = {
  title: 'Organisms/Toast',
  component: Toasts,
  tags: ['autodocs'],
  parameters: {
    layout: 'fullscreen'
  }
} satisfies StoryMeta<typeof Toasts>

export default Meta
type Story = StoryObj<typeof Meta>

/**
 * Shows all status variants and content combinations.
 */
export const AllVariants: Story = {
  render: (): JSX.Element => {
    const { addToast, clearToasts } = useToast()

    useEffect(() => {
      clearToasts()

      // Success variants
      addToast({
        status: 'success',
        title: 'Success Title',
        description: 'Success description text.',
        position: 'top-right'
      })

      // Failure variants
      addToast({
        status: 'failure',
        title: 'Error Occurred',
        description: 'A detailed error message explaining what went wrong.',
        position: 'top-right'
      })

      // Warning variants
      addToast({
        status: 'warning',
        title: 'Warning',
        description: 'This is a warning message.',
        position: 'top-right'
      })

      // Minimal
      addToast({
        status: 'success',
        title: 'Minimal Toast',
        position: 'top-right'
      })

      return (): void => clearToasts()
    }, [addToast, clearToasts])

    return <Toasts />
  }
}

/**
 * Demonstrates toasts with various content configurations.
 */
export const ContentVariants: Story = {
  render: (): JSX.Element => {
    const { addToast, clearToasts } = useToast()

    useEffect(() => {
      clearToasts()

      addToast({
        status: 'success',
        description: 'Toast without a title.',
        position: 'top-right'
      })
      addToast({
        status: 'success',
        title: 'Toast without a description',
        position: 'top-right'
      })
      addToast({
        status: 'failure',
        title: 'Not Dismissible',
        description: 'This toast cannot be closed manually.',
        dismissible: false,
        position: 'top-right'
      })
      addToast({
        status: 'warning',
        title:
          'Very long title that might wrap to multiple lines if the container is small enough',
        description:
          'This is a very long description to test how the toast component handles large amounts of text content. It should expand vertically to accommodate the text while maintaining its layout.',
        position: 'top-right'
      })

      return (): void => clearToasts()
    }, [addToast, clearToasts])

    return <Toasts />
  }
}

/**
 * Demonstrates auto-dismiss behavior.
 */
export const AutoDismiss: Story = {
  render: (): JSX.Element => {
    const { addToast, clearToasts } = useToast()

    useEffect(() => {
      clearToasts()

      addToast({
        status: 'success',
        title: 'Auto-dismiss (2s)',
        duration: 2000,
        position: 'top-right'
      })
      addToast({
        status: 'warning',
        title: 'Persistent Toast',
        duration: null,
        position: 'top-right'
      })

      return (): void => clearToasts()
    }, [addToast, clearToasts])

    return <Toasts />
  }
}

/**
 * Demonstrates toasts in different screen positions.
 */
export const Positions: Story = {
  render: (): JSX.Element => {
    const { addToast, clearToasts } = useToast()

    useEffect(() => {
      clearToasts()

      addToast({ status: 'success', title: 'Top Left', position: 'top-left' })
      addToast({ status: 'success', title: 'Top Center', position: 'top-center' })
      addToast({ status: 'success', title: 'Top Right', position: 'top-right' })
      addToast({ status: 'success', title: 'Bottom Left', position: 'bottom-left' })
      addToast({ status: 'success', title: 'Bottom Center', position: 'bottom-center' })
      addToast({ status: 'success', title: 'Bottom Right', position: 'bottom-right' })

      return (): void => clearToasts()
    }, [addToast, clearToasts])

    return <Toasts />
  }
}

/**
 * Interactive story for testing toast lifecycle and manual dismissal.
 */
export const Interactive: Story = {
  render: (): JSX.Element => {
    const { success, failure, warning, clearToasts } = useToast()

    return (
      <div style={{ padding: 24 }}>
        <Toasts />
        <Flex gap="m" wrap={true}>
          <Button
            onClick={() =>
              success({ title: 'Success', description: 'Operation completed' })
            }
          >
            Add Success
          </Button>
          <Button
            onClick={() => failure({ title: 'Error', description: 'Operation failed' })}
          >
            Add Failure
          </Button>
          <Button
            onClick={() => warning({ title: 'Warning', description: 'Check this out' })}
          >
            Add Warning
          </Button>
          <Button kind="secondary" onClick={clearToasts}>
            Clear All
          </Button>
        </Flex>
      </div>
    )
  },
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement)
    const body = within(document.body)

    // 1. Add a toast
    const successButton = canvas.getByRole('button', { name: /add success/i })
    await userEvent.click(successButton)

    // 2. Verify it appears
    const toast = await body.findByText('Operation completed')
    await expect(toast).toBeInTheDocument()
    await expect(body.getByText('Success')).toBeInTheDocument()

    // 3. Dismiss it
    const closeButton = body.getByLabelText('Close')
    await userEvent.click(closeButton)

    // 4. Verify it's removed after animation
    await new Promise((resolve) => setTimeout(resolve, 300))
    await expect(body.queryByText('Operation completed')).not.toBeInTheDocument()
  }
}
