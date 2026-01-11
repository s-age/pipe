import type { Meta as StoryMeta, StoryObj } from '@storybook/react-vite'
import { expect, fn, userEvent, within } from 'storybook/test'

import type {
  SessionOverview,
  SessionTreeNode
} from '@/lib/api/sessionTree/getSessionTree'

import { SessionList } from '../index'

const mockFlatSessions: SessionOverview[] = [
  {
    sessionId: 'session-1',
    purpose: 'Initial research on project requirements',
    background: 'Starting a new project',
    roles: ['Researcher'],
    procedure: 'Search for documentation',
    artifacts: ['requirements.md'],
    multiStepReasoningEnabled: false,
    tokenCount: 1250,
    lastUpdatedAt: '2024-01-10T10:00:00Z',
    deletedAt: ''
  },
  {
    sessionId: 'session-2',
    purpose: 'Implementation of core features',
    background: 'Requirements gathered',
    roles: ['Developer'],
    procedure: 'Write code and tests',
    artifacts: ['src/index.ts'],
    multiStepReasoningEnabled: true,
    tokenCount: 5400,
    lastUpdatedAt: '2024-01-10T11:30:00Z',
    deletedAt: ''
  }
]

const mockTreeSessions: SessionTreeNode[] = [
  {
    sessionId: 'parent-1',
    overview: {
      sessionId: 'parent-1',
      purpose: 'Main Project Thread',
      background: 'Project overview and coordination',
      roles: ['Lead'],
      procedure: 'Manage sub-tasks',
      artifacts: ['roadmap.md'],
      multiStepReasoningEnabled: true,
      tokenCount: 10000,
      lastUpdatedAt: '2024-01-10T09:00:00Z',
      deletedAt: ''
    },
    children: [
      {
        sessionId: 'child-1',
        overview: {
          sessionId: 'child-1',
          purpose: 'Sub-task: Database Setup',
          background: 'Setting up PostgreSQL',
          roles: ['DBA'],
          procedure: 'Run migrations',
          artifacts: ['schema.sql'],
          multiStepReasoningEnabled: false,
          tokenCount: 2500,
          lastUpdatedAt: '2024-01-10T09:15:00Z',
          deletedAt: ''
        },
        children: []
      },
      {
        sessionId: 'child-2',
        overview: {
          sessionId: 'child-2',
          purpose: 'Sub-task: API Design',
          background: 'Defining REST endpoints',
          roles: ['Architect'],
          procedure: 'Write OpenAPI spec',
          artifacts: ['api.yaml'],
          multiStepReasoningEnabled: false,
          tokenCount: 3000,
          lastUpdatedAt: '2024-01-10T09:45:00Z',
          deletedAt: ''
        },
        children: [
          {
            sessionId: 'grandchild-1',
            overview: {
              sessionId: 'grandchild-1',
              purpose: 'Endpoint: /users',
              background: 'User management endpoints',
              roles: ['Developer'],
              procedure: 'Implement CRUD',
              artifacts: ['users.ts'],
              multiStepReasoningEnabled: false,
              tokenCount: 1500,
              lastUpdatedAt: '2024-01-10T10:00:00Z',
              deletedAt: ''
            },
            children: []
          }
        ]
      }
    ]
  }
]

const Meta = {
  title: 'Organisms/SessionList',
  component: SessionList,
  tags: ['autodocs'],
  args: {
    onSelectAll: fn(),
    onSelectSession: fn()
  }
} satisfies StoryMeta<typeof SessionList>

export default Meta
type Story = StoryObj<typeof Meta>

/**
 * Flat list of sessions, typically used in search results or recent sessions.
 */
export const FlatList: Story = {
  args: {
    sessions: mockFlatSessions,
    selectedSessionIds: []
  }
}

/**
 * Hierarchical tree of sessions, showing parent-child relationships.
 */
export const Hierarchical: Story = {
  args: {
    sessions: mockTreeSessions,
    selectedSessionIds: []
  }
}

/**
 * Demonstrates the list with some sessions already selected.
 */
export const WithSelection: Story = {
  args: {
    sessions: mockFlatSessions,
    selectedSessionIds: ['session-1']
  }
}

/**
 * Tests the "Select All" interaction in the header.
 */
export const SelectAllInteraction: Story = {
  args: {
    sessions: mockFlatSessions,
    selectedSessionIds: []
  },
  play: async ({ args, canvasElement }) => {
    const canvas = within(canvasElement)

    // Find the "Select All" checkbox by its role and associated label text
    const selectAllCheckbox = canvas.getByRole('checkbox', { name: /subject/i })

    await userEvent.click(selectAllCheckbox)

    // Verify that onSelectAll was called with all sessions and isSelected=true
    await expect(args.onSelectAll).toHaveBeenCalledWith(mockFlatSessions, true)
  }
}

/**
 * Tests selecting an individual session.
 */
export const SelectSessionInteraction: Story = {
  args: {
    sessions: mockFlatSessions,
    selectedSessionIds: []
  },
  play: async ({ args, canvasElement }) => {
    const canvas = within(canvasElement)

    // Find the checkbox for the first session
    const sessionCheckbox = canvas.getByRole('checkbox', { name: /initial research/i })

    await userEvent.click(sessionCheckbox)

    // Verify that onSelectSession was called with the correct sessionId and isSelected=true
    await expect(args.onSelectSession).toHaveBeenCalledWith('session-1', true)
  }
}

/**
 * Tests archive sessions with filePath (line 55 coverage).
 * When useFilePath is true, uses filePath as identifier instead of sessionId.
 */
export const WithFilePath: Story = {
  args: {
    sessions: [
      {
        sessionId: 'archive-1',
        filePath: '/archives/session-2024-01-10.json',
        purpose: 'Archived session from Jan 10',
        background: 'Historical session',
        roles: ['Archivist'],
        procedure: 'Review',
        artifacts: [],
        multiStepReasoningEnabled: false,
        tokenCount: 800,
        lastUpdatedAt: '2024-01-10T08:00:00Z',
        deletedAt: ''
      }
    ] as SessionOverview[],
    selectedSessionIds: [],
    useFilePath: true
  },
  play: async ({ args, canvasElement }) => {
    const canvas = within(canvasElement)

    // Find the checkbox for the archived session
    const sessionCheckbox = canvas.getByRole('checkbox', { name: /archived session/i })

    await userEvent.click(sessionCheckbox)

    // Verify that onSelectSession was called with filePath instead of sessionId
    await expect(args.onSelectSession).toHaveBeenCalledWith(
      '/archives/session-2024-01-10.json',
      true
    )
  }
}
