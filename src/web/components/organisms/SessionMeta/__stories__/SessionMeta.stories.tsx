import type { Meta as StoryMeta, StoryObj } from '@storybook/react-vite'
import { http, HttpResponse } from 'msw'
import type { JSX } from 'react'
import { expect, fn, userEvent, waitFor, within } from 'storybook/test'

import { API_BASE_URL } from '@/constants/uri'
import type { SessionDetail } from '@/lib/api/session/getSession'
import { AppStoreProvider } from '@/stores/useAppStore'

import { SessionMeta } from '..'

const Meta = {
  title: 'Organisms/SessionMeta',
  component: SessionMeta,
  tags: ['autodocs'],
  decorators: [
    (Story): JSX.Element => (
      <AppStoreProvider>
        <Story />
      </AppStoreProvider>
    )
  ]
} satisfies StoryMeta<typeof SessionMeta>

export default Meta
type Story = StoryObj<typeof Meta>

const mockSessionDetail: SessionDetail = {
  sessionId: 'session_demo_001',
  purpose: 'Demo session for testing SessionMeta component',
  background: 'This is a demo background to test the component functionality',
  roles: ['developer', 'tester'],
  parent: null,
  references: [],
  artifacts: [],
  procedure: 'Step 1: Test\nStep 2: Verify\nStep 3: Deploy',
  instruction: '',
  multiStepReasoningEnabled: false,
  hyperparameters: {
    temperature: 0.7,
    topK: null,
    topP: null
  },
  todos: [],
  turns: []
}

export const Default: Story = {
  args: {
    sessionDetail: mockSessionDetail,
    onRefresh: fn(async () => Promise.resolve()),
    onSessionDetailUpdate: fn()
  }
}

/**
 * Demonstrates the save interaction with mocked API response.
 */
export const SaveInteraction: Story = {
  args: {
    sessionDetail: mockSessionDetail,
    onRefresh: fn(async () => Promise.resolve()),
    onSessionDetailUpdate: fn()
  },
  parameters: {
    msw: {
      handlers: [
        http.patch(`${API_BASE_URL}/session/${mockSessionDetail.sessionId}/meta`, () =>
          HttpResponse.json({ message: 'Session metadata saved' })
        )
      ]
    }
  },
  play: async ({ args, canvasElement }) => {
    const canvas = within(canvasElement)
    const saveButton = canvas.getByRole('button', {
      name: /save session metadata/i
    })

    // Click the save button
    await userEvent.click(saveButton)

    // Wait for loading state (aria-busy and text change)
    await waitFor(() => expect(saveButton).toHaveAttribute('aria-busy', 'true'))
    await waitFor(() => expect(saveButton).toHaveTextContent(/saving/i))

    // Wait for success message in status role
    const status = await canvas.findByRole('status')
    await expect(status).toHaveTextContent(/saved successfully/i)

    // Verify onRefresh was called after successful save
    await waitFor(() => expect(args.onRefresh).toHaveBeenCalled())
  }
}

/**
 * Demonstrates error handling when the save operation fails.
 */
export const SaveError: Story = {
  args: {
    sessionDetail: mockSessionDetail,
    onRefresh: fn(async () => Promise.resolve())
  },
  parameters: {
    msw: {
      handlers: [
        http.patch(
          `${API_BASE_URL}/session/${mockSessionDetail.sessionId}/meta`,
          () => new HttpResponse(null, { status: 500 })
        )
      ]
    }
  },
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement)
    const saveButton = canvas.getByRole('button', {
      name: /save session metadata/i
    })

    // Click the save button
    await userEvent.click(saveButton)

    // Wait for error message in status role
    const status = await canvas.findByRole('status')
    await expect(status).toHaveTextContent(/failed to save/i)
  }
}

/**
 * Demonstrates the component with minimal data.
 */
export const MinimalData: Story = {
  args: {
    sessionDetail: {
      ...mockSessionDetail,
      purpose: '',
      background: '',
      roles: [],
      procedure: null,
      artifacts: [],
      hyperparameters: null
    },
    onRefresh: fn(async () => Promise.resolve())
  }
}
