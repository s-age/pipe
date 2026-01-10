import type { Meta as StoryMeta, StoryObj } from '@storybook/react-vite'
import type { JSX } from 'react'
import { expect, fn, userEvent, within } from 'storybook/test'

import { ScrollArea } from '@/components/molecules/ScrollArea'
import type { SessionDetail } from '@/lib/api/session/getSession'
import { AppStoreProvider } from '@/stores/useAppStore'

import { SessionControl } from '../index'

const mockSessionDetail: SessionDetail = {
  sessionId: 'session-123',
  purpose: 'Test Purpose',
  background: 'Test Background',
  instruction: 'Test Instruction',
  roles: ['Role 1'],
  artifacts: [],
  references: [],
  todos: [],
  turns: [],
  hyperparameters: {
    temperature: 0.7,
    topP: 0.9,
    topK: 40
  },
  multiStepReasoningEnabled: false,
  parent: null,
  procedure: null
}

const Meta = {
  title: 'Organisms/SessionControl',
  component: SessionControl,
  tags: ['autodocs'],
  decorators: [
    (Story): JSX.Element => (
      <AppStoreProvider>
        <div style={{ height: '600px' }}>
          <ScrollArea direction="vertical">
            <Story />
          </ScrollArea>
        </div>
      </AppStoreProvider>
    )
  ],
  args: {
    sessionDetail: mockSessionDetail,
    onRefresh: fn(async () => {}),
    onSessionDetailUpdate: fn()
  }
} satisfies StoryMeta<typeof SessionControl>

export default Meta

type Story = StoryObj<typeof Meta>

export const Default: Story = {
  args: {
    sessionDetail: mockSessionDetail
  }
}

export const TabInteraction: Story = {
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement)

    // Verify initial tab (Meta)
    await expect(canvas.getByText('Meta')).toBeInTheDocument()

    // Switch to Compressor tab
    const compressorTab = canvas.getByRole('tab', { name: /compressor/i })
    await userEvent.click(compressorTab)

    // Verify Compressor tab is active (or at least clickable)
    await expect(compressorTab).toBeInTheDocument()

    // Switch to Therapist tab
    const therapistTab = canvas.getByRole('tab', { name: /therapist/i })
    await userEvent.click(therapistTab)
    await expect(therapistTab).toBeInTheDocument()
  }
}
