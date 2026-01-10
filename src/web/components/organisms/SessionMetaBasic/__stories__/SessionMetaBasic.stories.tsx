import type { Meta as StoryMeta, StoryObj } from '@storybook/react-vite'
import type { JSX } from 'react'
import { expect, userEvent, within } from 'storybook/test'

import { Form } from '@/components/organisms/Form'
import type { SessionDetail } from '@/lib/api/session/getSession'

import { SessionMetaBasic } from '../index'

const mockSessionDetail: SessionDetail = {
  sessionId: 'test-session-id',
  purpose: 'Test Purpose',
  background: 'Test Background',
  roles: ['role-1'],
  procedure: 'procedure-1',
  artifacts: [],
  references: [],
  todos: [],
  turns: [],
  multiStepReasoningEnabled: false,
  hyperparameters: null,
  instruction: 'Test Instruction',
  parent: null
}

const Meta = {
  title: 'Organisms/SessionMetaBasic',
  component: SessionMetaBasic,
  tags: ['autodocs'],
  decorators: [
    (Story): JSX.Element => (
      <Form defaultValues={mockSessionDetail}>
        <Story />
      </Form>
    )
  ]
} satisfies StoryMeta<typeof SessionMetaBasic>

export default Meta
type Story = StoryObj<typeof Meta>

/**
 * Default story for SessionMetaBasic
 */
export const Default: Story = {
  args: {
    sessionDetail: mockSessionDetail
  }
}

/**
 * Story demonstrating SessionMetaBasic with children
 */
export const WithChildren: Story = {
  args: {
    sessionDetail: mockSessionDetail,
    children: (
      <div
        style={{
          padding: '12px',
          marginTop: '12px',
          border: '1px dashed #666',
          color: '#ccc',
          textAlign: 'center'
        }}
      >
        Additional Meta Content (Children)
      </div>
    )
  }
}

/**
 * Interaction test for SessionMetaBasic
 */
export const Interaction: Story = {
  args: {
    sessionDetail: mockSessionDetail
  },
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement)

    // Verify Purpose field
    const purposeInput = canvas.getByRole('textbox', { name: /purpose/i })
    await expect(purposeInput).toBeInTheDocument()
    await userEvent.clear(purposeInput)
    await userEvent.type(purposeInput, 'Updated Purpose')
    await expect(purposeInput).toHaveValue('Updated Purpose')

    // Verify Background field
    const backgroundInput = canvas.getByRole('textbox', { name: /background/i })
    await expect(backgroundInput).toBeInTheDocument()
    await userEvent.clear(backgroundInput)
    await userEvent.type(backgroundInput, 'Updated Background')
    await expect(backgroundInput).toHaveValue('Updated Background')
  }
}
