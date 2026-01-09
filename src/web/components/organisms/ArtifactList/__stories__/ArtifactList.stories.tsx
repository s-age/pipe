import type { Meta as StoryMeta, StoryObj } from '@storybook/react-vite'
import type { JSX } from 'react'

import { Form } from '@/components/organisms/Form'
import type { SessionDetail } from '@/lib/api/session/getSession'

import { ArtifactList } from '../index'

const mockSessionDetail: SessionDetail = {
  artifacts: ['src/index.ts', 'src/utils.ts'],
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
  title: 'Organisms/ArtifactList',
  component: ArtifactList,
  tags: ['autodocs']
} satisfies StoryMeta<typeof ArtifactList>

export default Meta

type Story = StoryObj<typeof Meta>

export const Default: Story = {
  args: {
    sessionDetail: mockSessionDetail,
    refreshSessions: async () => {
      console.log('refreshSessions called')
    }
  }
}

export const WithForm: Story = {
  render: (arguments_): JSX.Element => (
    <Form defaultValues={{ artifacts: arguments_.sessionDetail.artifacts }}>
      <ArtifactList {...arguments_} />
    </Form>
  ),
  args: {
    sessionDetail: mockSessionDetail,
    refreshSessions: async () => {
      console.log('refreshSessions called')
    }
  }
}

export const Empty: Story = {
  args: {
    sessionDetail: {
      ...mockSessionDetail,
      artifacts: []
    },
    refreshSessions: async () => {
      console.log('refreshSessions called')
    }
  }
}
