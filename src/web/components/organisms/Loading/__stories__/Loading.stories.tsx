import type { Meta as StoryMeta, StoryObj } from '@storybook/react-vite'
import React, { useEffect } from 'react'
import type { JSX } from 'react'
import { expect, userEvent, within } from 'storybook/test'

import { AppStoreProvider, useAppStore } from '@/stores/useAppStore'

import { LoadingOverlay } from '../index'

const Wrapper = ({ children }: React.PropsWithChildren<unknown>): JSX.Element => (
  <AppStoreProvider>
    {children}
    <LoadingOverlay />
  </AppStoreProvider>
)

const Meta = {
  title: 'Organisms/Loading',
  component: LoadingOverlay,
  decorators: [
    (Story: () => JSX.Element): JSX.Element => (
      <Wrapper>
        <Story />
      </Wrapper>
    )
  ],
  tags: ['autodocs']
} satisfies StoryMeta<typeof LoadingOverlay>

export default Meta
type Story = StoryObj<typeof Meta>

const Controls = (): JSX.Element => {
  const { hideLoader, showLoader } = useAppStore()

  const start = async (): Promise<void> => {
    showLoader()
    // simulate async work
    await new Promise((r) => setTimeout(r, 1200))
    hideLoader()
  }

  return (
    <div style={{ display: 'flex', gap: 8 }}>
      <button type="button" onClick={() => showLoader()}>
        Show
      </button>
      <button type="button" onClick={() => hideLoader()}>
        Hide
      </button>
      <button type="button" onClick={start}>
        Simulate async
      </button>
    </div>
  )
}

/**
 * Default story with manual controls to toggle the loading state.
 */
export const Default: Story = {
  render: (): JSX.Element => <Controls />
}

/**
 * Story that automatically shows the loading overlay on mount.
 */
export const Visible: Story = {
  render: (): JSX.Element => {
    const AutoShow = (): JSX.Element => {
      const { showLoader } = useAppStore()
      useEffect(() => {
        showLoader()
      }, [showLoader])

      return <Controls />
    }

    return <AutoShow />
  }
}

/**
 * Interaction test verifying that the loading overlay appears and disappears correctly.
 */
export const Interaction: Story = {
  render: (): JSX.Element => <Controls />,
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement)
    const showButton = canvas.getByRole('button', { name: /show/i })
    const hideButton = canvas.getByRole('button', { name: /hide/i })

    // Click show and verify overlay presence
    await userEvent.click(showButton)
    // The overlay is rendered as a sibling to the story content within the decorator's Wrapper.
    // We search in the parent element to ensure we find the overlay if it's outside the story root.
    const root = canvasElement.parentElement || canvasElement
    const overlay = await within(root).findByRole('status', { name: /loading/i })
    await expect(overlay).toBeInTheDocument()

    // Click hide and verify overlay is removed
    await userEvent.click(hideButton)
    await expect(overlay).not.toBeInTheDocument()
  }
}
