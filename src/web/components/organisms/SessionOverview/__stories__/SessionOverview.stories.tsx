import type { Meta as StoryMeta, StoryObj } from '@storybook/react-vite'
import type { JSX } from 'react'
import { MemoryRouter } from 'react-router-dom'
import { expect, fn, userEvent, within } from 'storybook/test'

import type { SessionOverview as SessionOverviewType } from '@/lib/api/sessionTree/getSessionTree'

import { SessionOverviewComponent } from '../index'

const Meta = {
  title: 'Organisms/SessionOverview',
  component: SessionOverviewComponent,
  tags: ['autodocs'],
  decorators: [
    (Story): JSX.Element => (
      <MemoryRouter>
        <Story />
      </MemoryRouter>
    )
  ],
  args: {
    handleSelectSession: fn()
  }
} satisfies StoryMeta<typeof SessionOverviewComponent>

export default Meta
type Story = StoryObj<typeof Meta>

const baseSession: SessionOverviewType = {
  sessionId: 'session-1234567890',
  purpose: 'Test Session Purpose',
  artifacts: [],
  background: 'Test background',
  lastUpdatedAt: new Date().toISOString(),
  multiStepReasoningEnabled: false,
  procedure: 'Test procedure',
  roles: [],
  tokenCount: 100
}

/**
 * Default state of the session overview item.
 */
export const Default: Story = {
  args: {
    currentSessionId: 'other-session-id',
    session: baseSession
  }
}

/**
 * Active state when the session is currently selected.
 */
export const Active: Story = {
  args: {
    currentSessionId: 'session-active-id',
    session: {
      ...baseSession,
      sessionId: 'session-active-id',
      purpose: 'Active Session'
    }
  }
}

/**
 * Edge case with a very long purpose text.
 */
export const LongPurpose: Story = {
  args: {
    currentSessionId: 'other-session-id',
    session: {
      ...baseSession,
      sessionId: 'session-long-id',
      purpose:
        'This is a very long session purpose to test how the component handles text wrapping and layout when the content exceeds the normal width of the sidebar or container.'
    }
  }
}

/**
 * Interaction test to verify that clicking the session link triggers the selection handler.
 */
export const Interaction: Story = {
  args: {
    currentSessionId: 'other-session-id',
    session: {
      ...baseSession,
      sessionId: 'session-interaction-id',
      purpose: 'Click Me'
    }
  },
  play: async ({ args, canvasElement }) => {
    const canvas = within(canvasElement)
    const link = canvas.getByRole('link', { name: /click me/i })

    await userEvent.click(link)
    await expect(args.handleSelectSession).toHaveBeenCalledWith(
      'session-interaction-id'
    )
  }
}
