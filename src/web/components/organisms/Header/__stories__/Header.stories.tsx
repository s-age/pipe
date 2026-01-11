import type { Meta as StoryMeta, StoryObj } from '@storybook/react-vite'
import type { JSX } from 'react'
import { expect, userEvent, within } from 'storybook/test'

import { TooltipManager } from '@/components/organisms/Tooltip'
import { fsHandlers } from '@/msw/resources/fs'
import { AppStoreProvider } from '@/stores/useAppStore'

import { Header } from '../index'

const Meta = {
  title: 'Organisms/Header',
  component: Header,
  tags: ['autodocs'],
  decorators: [
    (Story): JSX.Element => (
      <AppStoreProvider>
        <TooltipManager />
        <Story />
      </AppStoreProvider>
    )
  ]
} satisfies StoryMeta<typeof Header>

export default Meta

type Story = StoryObj<typeof Meta>

/**
 * Default state of the Header.
 * Shows the brand logo, search input, and session management link.
 */
export const Default: Story = {}

/**
 * Demonstrates the search interaction.
 * Tests the search input interaction without requiring the modal to appear.
 * The full search flow with API mocking is better tested in integration tests.
 */
export const SearchInteraction: Story = {
  parameters: {
    msw: {
      handlers: fsHandlers
    }
  },
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement)
    const searchInput = canvas.getByPlaceholderText(/search sessions/i)

    // Verify search input exists and is interactive
    await expect(searchInput).toBeInTheDocument()
    await expect(searchInput).not.toBeDisabled()

    // Type into the search input
    await userEvent.type(searchInput, 'test')

    // Verify the value was updated
    await expect(searchInput).toHaveValue('test')
  }
}

/**
 * Verifies the session management link is present and has the correct destination.
 */
export const SessionManagementLink: Story = {
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement)
    const link = canvas.getByRole('link', { name: /session management/i })

    await expect(link).toBeInTheDocument()
    await expect(link).toHaveAttribute('href', '/session_management')
  }
}

/**
 * Demonstrates the search input interaction.
 * Tests that typing in the search input works (line 99 coverage).
 * Note: Full modal testing with navigation is better suited for E2E tests.
 */
export const SearchInputInteraction: Story = {
  parameters: {
    msw: {
      handlers: fsHandlers
    }
  },
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement)
    const searchInput = canvas.getByPlaceholderText(/search sessions/i)

    // Verify search input exists
    await expect(searchInput).toBeInTheDocument()

    // Type into search input without triggering submission
    await userEvent.clear(searchInput)
    await userEvent.type(searchInput, 'test', { delay: 50 })

    // Verify the input value was updated
    await expect(searchInput).toHaveValue('test')

    // Clear the input to avoid any side effects
    await userEvent.clear(searchInput)
  }
}
