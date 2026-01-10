import type { Meta as StoryMeta, StoryObj } from '@storybook/react-vite'
import { http, HttpResponse } from 'msw'
import type { JSX } from 'react'
import { expect, userEvent, waitFor, within } from 'storybook/test'

import { API_BASE_URL } from '@/constants/uri'
import { AppStoreProvider } from '@/stores/useAppStore'

import { RolesSelect } from '../index'

const mockRoles = [
  { label: 'Admin', value: 'admin' },
  { label: 'Editor', value: 'editor' },
  { label: 'Viewer', value: 'viewer' }
]

const mockSession = {
  artifacts: [],
  background: 'Test background',
  hyperparameters: null,
  instruction: 'Test instruction',
  multiStepReasoningEnabled: false,
  parent: null,
  procedure: null,
  purpose: 'Test purpose',
  references: [],
  roles: [],
  sessionId: 'test-session-id',
  todos: [],
  turns: []
}

const Meta = {
  title: 'Organisms/RolesSelect',
  component: RolesSelect,
  tags: ['autodocs'],
  decorators: [
    (Story): JSX.Element => (
      <AppStoreProvider>
        <Story />
      </AppStoreProvider>
    )
  ],
  parameters: {
    msw: {
      handlers: [
        http.get(`${API_BASE_URL}/fs/roles`, () =>
          HttpResponse.json({ roles: mockRoles })
        )
      ]
    }
  }
} satisfies StoryMeta<typeof RolesSelect>

export default Meta

type Story = StoryObj<typeof Meta>

export const Default: Story = {
  args: {
    sessionDetail: mockSession,
    placeholder: 'Select roles...'
  }
}

export const WithSelectedRoles: Story = {
  args: {
    sessionDetail: {
      ...mockSession,
      roles: ['admin', 'editor']
    },
    placeholder: 'Select roles...'
  }
}

export const Interaction: Story = {
  args: {
    sessionDetail: mockSession,
    placeholder: 'Select roles...'
  },
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement)
    const input = canvas.getByPlaceholderText('Search files or directories...')

    // Focus and type to trigger role filtering
    await userEvent.click(input)
    await userEvent.type(input, 'Ad')

    // Wait for the suggestion list to appear and roles to be loaded
    await waitFor(
      async () => {
        const listbox = canvas.getByRole('listbox')
        expect(listbox).toBeInTheDocument()
      },
      { timeout: 3000 }
    )

    // Wait for roles to be loaded and displayed in the list
    // FileSearchExplorer renders a list of items. We expect 'Admin' to appear.
    const adminOption = await canvas.findByText('Admin')
    await expect(adminOption).toBeInTheDocument()

    // Select a role
    await userEvent.click(adminOption)

    // Verify selection - Admin should appear as a tag in PathDisplay
    // After selection, the item should be in the pathDisplayContainer
    await waitFor(() => {
      const tags = canvas.getAllByText('admin')
      // There should be at least one tag with the selected role
      expect(tags.length).toBeGreaterThan(0)
    })
  }
}
