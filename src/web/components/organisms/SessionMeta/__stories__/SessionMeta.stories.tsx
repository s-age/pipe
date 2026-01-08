import type { Meta as StoryMeta, StoryObj } from '@storybook/react-vite'
import type { JSX } from 'react'

import type { SessionDetail } from '@/lib/api/session/getSession'

import { SessionMeta } from '..'

const Meta = {
  title: 'Organisms/SessionMeta',
  component: SessionMeta,
  tags: ['autodocs']
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

const mockOnRefresh = async (): Promise<void> => {
  console.log('Refresh called')

  return Promise.resolve()
}

const mockOnSessionDetailUpdate = (updatedDetail: SessionDetail): void => {
  console.log('Session detail updated:', updatedDetail)
}

export const Default: Story = {
  args: {
    sessionDetail: mockSessionDetail,
    onRefresh: mockOnRefresh,
    onSessionDetailUpdate: mockOnSessionDetailUpdate
  }
}

const ariaSessionDetail: SessionDetail = {
  sessionId: 'session_aria_demo',
  purpose: 'Demonstrating ARIA attributes',
  background: 'This story demonstrates the ARIA attributes implementation',
  roles: ['developer'],
  parent: null,
  references: [],
  artifacts: [],
  procedure: null,
  instruction: '',
  multiStepReasoningEnabled: false,
  hyperparameters: null,
  todos: [],
  turns: []
}

const ariaOnRefresh = async (): Promise<void> => {
  // Simulate async refresh
  await new Promise((resolve) => setTimeout(resolve, 1000))
  console.log('Refresh completed')
}

export const WithAriaAttributes: Story = {
  args: {
    sessionDetail: ariaSessionDetail,
    onRefresh: ariaOnRefresh
  },
  decorators: [
    (Story): JSX.Element => (
      <div style={{ height: '600px', display: 'flex' }}>
        <div style={{ flex: 1 }}>
          <Story />
        </div>
        <div style={{ padding: '16px', borderLeft: '1px solid #eee', width: '300px' }}>
          <h3>ARIA Features:</h3>
          <ul style={{ fontSize: '14px', lineHeight: '1.6' }}>
            <li>
              <strong>aria-label</strong>: Save button has descriptive label &quot;Save
              session metadata&quot;
            </li>
            <li>
              <strong>aria-busy</strong>: Indicates when save operation is in progress
            </li>
            <li>
              <strong>role=&quot;status&quot;</strong>: Announces save success/failure
              to screen readers
            </li>
          </ul>
          <p style={{ fontSize: '12px', color: '#666', marginTop: '16px' }}>
            Try clicking the &quot;Save Meta&quot; button and observe the aria-busy
            state and status announcements.
          </p>
        </div>
      </div>
    )
  ]
}
