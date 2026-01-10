import type { Meta as StoryMeta, StoryObj } from '@storybook/react-vite'
import type { JSX } from 'react'
import { MemoryRouter } from 'react-router-dom'
import { expect, fn, userEvent, within } from 'storybook/test'

import type {
  SessionOverview,
  SessionTreeNode
} from '@/lib/api/sessionTree/getSessionTree'

import { SessionTree } from '../index'

const Meta = {
  title: 'Organisms/SessionTree',
  component: SessionTree,
  tags: ['autodocs'],
  decorators: [
    (Story): JSX.Element => (
      <MemoryRouter>
        <Story />
      </MemoryRouter>
    )
  ],
  args: {
    handleSelectSession: fn().mockImplementation(() => Promise.resolve()),
    onRefresh: fn().mockImplementation(() => Promise.resolve())
  }
} satisfies StoryMeta<typeof SessionTree>

export default Meta
type Story = StoryObj<typeof Meta>

const mockSessions: SessionOverview[] = [
  {
    sessionId: 'session-1',
    purpose: 'Research on AI agents',
    background: 'Background info',
    roles: ['Researcher'],
    procedure: 'Step 1...',
    artifacts: ['Report.pdf'],
    multiStepReasoningEnabled: false,
    tokenCount: 100,
    lastUpdatedAt: new Date().toISOString()
  },
  {
    sessionId: 'session-2',
    purpose: 'Development of Storybook stories',
    background: 'Coding task',
    roles: ['Developer'],
    procedure: 'Write stories...',
    artifacts: ['stories.tsx'],
    multiStepReasoningEnabled: true,
    tokenCount: 500,
    lastUpdatedAt: new Date().toISOString()
  }
]

const mockTreeSessions: SessionTreeNode[] = [
  {
    sessionId: 'parent-1',
    overview: {
      sessionId: 'parent-1',
      purpose: 'Parent Session 1',
      background: '',
      roles: [],
      procedure: '',
      artifacts: [],
      multiStepReasoningEnabled: false,
      tokenCount: 0,
      lastUpdatedAt: new Date().toISOString()
    },
    children: [
      {
        sessionId: 'child-1-1',
        overview: {
          sessionId: 'child-1-1',
          purpose: 'Child Session 1.1',
          background: '',
          roles: [],
          procedure: '',
          artifacts: [],
          multiStepReasoningEnabled: false,
          tokenCount: 0,
          lastUpdatedAt: new Date().toISOString()
        },
        children: []
      }
    ]
  },
  {
    sessionId: 'parent-2',
    overview: {
      sessionId: 'parent-2',
      purpose: 'Parent Session 2',
      background: '',
      roles: [],
      procedure: '',
      artifacts: [],
      multiStepReasoningEnabled: false,
      tokenCount: 0,
      lastUpdatedAt: new Date().toISOString()
    },
    children: []
  }
]

/**
 * Default view with a flat list of sessions.
 */
export const Default: Story = {
  args: {
    sessions: mockSessions,
    currentSessionId: 'session-1'
  },
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement)

    // Verify sessions are rendered
    await expect(canvas.getByText(/Research on AI agents/i)).toBeInTheDocument()
    await expect(
      canvas.getByText(/Development of Storybook stories/i)
    ).toBeInTheDocument()

    // Verify active state (session-1)
    const activeLink = canvas.getByRole('link', { name: /Research on AI agents/i })
    await expect(activeLink).toBeInTheDocument()
  }
}

/**
 * Hierarchical view with nested session nodes.
 */
export const Hierarchical: Story = {
  args: {
    sessions: mockTreeSessions,
    currentSessionId: 'child-1-1'
  },
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement)

    // Verify parent and child are rendered
    await expect(canvas.getByText(/Parent Session 1/i)).toBeInTheDocument()
    await expect(canvas.getByText(/Child Session 1.1/i)).toBeInTheDocument()
    await expect(canvas.getByText(/Parent Session 2/i)).toBeInTheDocument()
  }
}

/**
 * Empty state when no sessions are available.
 */
export const Empty: Story = {
  args: {
    sessions: [],
    currentSessionId: null
  },
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement)

    // Verify "New Chat" button is still there
    await expect(canvas.getByRole('button', { name: /New Chat/i })).toBeInTheDocument()

    // Verify no session links are present
    const links = canvas.queryAllByRole('link')
    // The "New Chat" button is a Button component, which renders as <button> by default.
    // Session links are Link components, which render as <a>.
    expect(links.length).toBe(0)
  }
}

/**
 * Interaction test for selecting a session in the flat list.
 */
export const SelectionInteraction: Story = {
  args: {
    sessions: mockSessions,
    currentSessionId: 'session-1'
  },
  play: async ({ args, canvasElement }) => {
    const canvas = within(canvasElement)

    const secondSession = canvas.getByText(/Development of Storybook stories/i)
    await userEvent.click(secondSession)

    // handleSelectSession should be called with the correct sessionId
    await expect(args.handleSelectSession).toHaveBeenCalledWith('session-2')
  }
}
