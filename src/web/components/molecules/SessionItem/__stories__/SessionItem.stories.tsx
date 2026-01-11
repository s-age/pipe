import type { Meta as StoryMeta, StoryObj } from '@storybook/react-vite'
import { expect, fn, userEvent, within } from 'storybook/test'

import type {
  SessionOverview,
  SessionTreeNode
} from '@/lib/api/sessionTree/getSessionTree'

import { SessionItem } from '../index'

const Meta = {
  title: 'Molecules/SessionItem',
  component: SessionItem,
  tags: ['autodocs'],
  args: {
    onSelect: fn()
  }
} satisfies StoryMeta<typeof SessionItem>

export default Meta
type Story = StoryObj<typeof Meta>

const mockSessionOverview: SessionOverview = {
  sessionId: 'session-1234567890',
  purpose: 'Regular Session Overview',
  lastUpdatedAt: '2023-10-01T12:00:00Z',
  artifacts: [],
  background: 'Test background',
  multiStepReasoningEnabled: false,
  procedure: 'Test procedure',
  roles: [],
  tokenCount: 100
}

const mockSessionTreeNode: SessionTreeNode = {
  sessionId: 'tree-0987654321',
  overview: {
    ...mockSessionOverview,
    sessionId: 'tree-0987654321',
    purpose: 'Session from Tree Node',
    lastUpdatedAt: '2023-10-02T15:30:00Z'
  },
  children: []
}

const mockDeletedSession: SessionOverview = {
  ...mockSessionOverview,
  sessionId: 'deleted-777',
  purpose: 'Deleted Session Item',
  deletedAt: '2023-10-05T10:00:00Z'
}

const mockArchiveSession: SessionOverview = {
  ...mockSessionOverview,
  sessionId: 'archive-888',
  purpose: 'Archive Session with File Path',
  filePath: '/home/user/projects/archive-2023.zip',
  lastUpdatedAt: '2023-10-10T08:00:00Z'
}

// 1. Default
export const Default: Story = {
  args: {
    isSelected: false,
    session: mockSessionOverview
  }
}

// 2. Selected
export const Selected: Story = {
  args: {
    isSelected: true,
    session: mockSessionOverview
  }
}

// 3. TreeNode
export const TreeNode: Story = {
  args: {
    isSelected: false,
    session: mockSessionTreeNode
  }
}

// 4. DeletedAt
export const DeletedAt: Story = {
  args: {
    isSelected: false,
    session: mockDeletedSession,
    updateLabel: 'Deleted At'
  }
}

// 5. UseFilePath
export const UseFilePath: Story = {
  args: {
    isSelected: false,
    session: mockArchiveSession,
    useFilePath: true
  }
}

// 6. LongPurpose
export const LongPurpose: Story = {
  args: {
    isSelected: false,
    session: {
      ...mockSessionOverview,
      purpose:
        'This is an extremely long session purpose to test how the component handles text overflow and wrapping in the grid layout. It should ideally truncate or wrap gracefully without breaking the layout.'
    }
  }
}

// 7. UnknownDate
export const UnknownDate: Story = {
  args: {
    isSelected: false,
    session: {
      ...mockSessionOverview,
      lastUpdatedAt: ''
    }
  }
}

// 8. Interaction
export const Interaction: Story = {
  args: {
    isSelected: false,
    session: mockSessionOverview
  },
  play: async ({ args, canvasElement }) => {
    const canvas = within(canvasElement)
    const checkbox = canvas.getByRole('checkbox')

    await userEvent.click(checkbox)
    await expect(args.onSelect).toHaveBeenCalledWith(
      mockSessionOverview.sessionId,
      true
    )
  }
}

// 9. UnknownSessionId
export const UnknownSessionId: Story = {
  args: {
    isSelected: false,
    session: {
      ...mockSessionOverview,
      sessionId: ''
    }
  },
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement)
    const checkbox = canvas.getByRole('checkbox')
    await expect(checkbox).toHaveAttribute('id', 'session-unknown')
  }
}

// 10. TreeNodeWithDeletedAt
export const TreeNodeWithDeletedAt: Story = {
  args: {
    isSelected: false,
    session: {
      ...mockSessionTreeNode,
      overview: {
        ...mockSessionTreeNode.overview,
        deletedAt: '2023-10-15T16:00:00Z'
      }
    },
    updateLabel: 'Deleted At'
  },
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement)
    const dateText = canvas.getByText(/2023-10-15/)
    await expect(dateText).toBeInTheDocument()
  }
}

// 11. OverviewWithoutPurpose
export const OverviewWithoutPurpose: Story = {
  args: {
    isSelected: false,
    session: {
      ...mockSessionTreeNode,
      overview: {
        ...mockSessionTreeNode.overview,
        purpose: ''
      }
    }
  },
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement)
    const unknownText = canvas.getByText(/unknown/i)
    await expect(unknownText).toBeInTheDocument()
  }
}

// 12. TreeNodeDeletedAtFallback
/**
 * Tests TreeNode with Deleted At label but no deletedAt in overview (lines 52-53 coverage).
 */
export const TreeNodeDeletedAtFallback: Story = {
  args: {
    isSelected: false,
    session: {
      ...mockSessionTreeNode,
      overview: {
        ...mockSessionTreeNode.overview
        // No deletedAt field
      }
    },
    updateLabel: 'Deleted At'
  },
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement)
    // Should fallback to empty string, then formatDate handles it as 'Unknown'
    const unknownText = canvas.getByText(/unknown/i)
    await expect(unknownText).toBeInTheDocument()
  }
}

// 13. OverviewDeletedAtFallback
/**
 * Tests SessionOverview with Deleted At label but no deletedAt field (line 53 coverage).
 */
export const OverviewDeletedAtFallback: Story = {
  args: {
    isSelected: false,
    session: {
      ...mockSessionOverview
      // No deletedAt field
    },
    updateLabel: 'Deleted At'
  },
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement)
    const unknownText = canvas.getByText(/unknown/i)
    await expect(unknownText).toBeInTheDocument()
  }
}

// 14. TreeNodeUpdateAtFallback
/**
 * Tests TreeNode with Updated At label but no lastUpdatedAt in overview (line 55 coverage).
 */
export const TreeNodeUpdateAtFallback: Story = {
  args: {
    isSelected: false,
    session: {
      ...mockSessionTreeNode,
      overview: {
        ...mockSessionTreeNode.overview,
        lastUpdatedAt: ''
      }
    },
    updateLabel: 'Updated At'
  },
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement)
    const unknownText = canvas.getByText(/unknown/i)
    await expect(unknownText).toBeInTheDocument()
  }
}
