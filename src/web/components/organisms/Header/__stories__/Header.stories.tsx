import type { Meta as StoryMeta, StoryObj } from '@storybook/react-vite'
import type { JSX } from 'react'
import { expect, userEvent, within } from 'storybook/test'

import { TooltipManager } from '@/components/organisms/Tooltip'
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
 * Typing in the search input opens the results modal.
 */
export const SearchInteraction: Story = {
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement)
    const searchInput = canvas.getByPlaceholderText(/search sessions/i)

    await userEvent.type(searchInput, 'test')

    // Wait for debounce (default 300ms in useSearchSessionsLifecycle) and modal to appear
    // The modal only opens if there are search results
    const modal = await canvas.findByRole('dialog', {}, { timeout: 3000 })
    await expect(modal).toBeInTheDocument()
    await expect(within(modal).getByText(/search results/i)).toBeInTheDocument()
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
