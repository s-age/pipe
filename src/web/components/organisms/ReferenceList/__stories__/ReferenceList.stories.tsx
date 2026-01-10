import type { Meta as StoryMeta, StoryObj } from '@storybook/react-vite'
import type { JSX } from 'react'
import { expect, fn, userEvent, waitFor, within } from 'storybook/test'

import type { SessionDetail } from '@/lib/api/session/getSession'
import { AppStoreProvider } from '@/stores/useAppStore'

import { ReferenceList } from '../index'

const Meta = {
  title: 'Organisms/ReferenceList',
  component: ReferenceList,
  tags: ['autodocs'],
  decorators: [
    (Story): JSX.Element => (
      <AppStoreProvider>
        <div
          style={{ padding: '20px', backgroundColor: '#1e1e1e', minHeight: '400px' }}
        >
          <Story />
        </div>
      </AppStoreProvider>
    )
  ],
  args: {
    refreshSessions: fn()
  }
} satisfies StoryMeta<typeof ReferenceList>

export default Meta
type Story = StoryObj<typeof Meta>

/**
 * Default state with existing references.
 */
export const Default: Story = {
  args: {
    sessionDetail: {
      sessionId: 'session-123',
      references: [
        {
          path: 'src/web/components/organisms/ReferenceList/index.tsx',
          disabled: false,
          ttl: 3,
          persist: false
        },
        {
          path: 'src/web/components/organisms/ReferenceList/style.css.ts',
          disabled: true,
          ttl: 5,
          persist: true
        }
      ]
    } as unknown as SessionDetail
  },
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement)

    // Verify label
    await expect(canvas.getByText(/References:/i)).toBeInTheDocument()

    // Verify summary text
    await expect(canvas.getByText(/2 references/i)).toBeInTheDocument()

    // Open accordion to see details
    const accordionTrigger = canvas.getByRole('button', { expanded: false })
    await userEvent.click(accordionTrigger)

    // Wait for and verify reference paths are displayed using data-testid
    await waitFor(() => {
      const referencePaths = canvas.getAllByTestId('reference-path')
      expect(referencePaths).toHaveLength(2)
      expect(referencePaths[0]).toHaveTextContent(
        'src/web/components/organisms/ReferenceList/index.tsx'
      )
      expect(referencePaths[1]).toHaveTextContent(
        'src/web/components/organisms/ReferenceList/style.css.ts'
      )
    })
  }
}

/**
 * Empty state with no references.
 */
export const Empty: Story = {
  args: {
    sessionDetail: {
      sessionId: 'session-456',
      references: []
    } as unknown as SessionDetail
  },
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement)

    // Verify summary text for 0 references
    await expect(canvas.getByText(/0 references/i)).toBeInTheDocument()

    // Accordion is already open by default, so just verify the empty message
    await expect(canvas.getByText('No references added yet.')).toBeInTheDocument()
  }
}
