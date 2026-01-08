import type { Meta as StoryMeta, StoryObj } from '@storybook/react-vite'
import type { JSX } from 'react'

import { SessionMeta } from '..'

const Meta = {
  title: 'Organisms/SessionMeta',
  component: SessionMeta,
  tags: ['autodocs']
} satisfies StoryMeta<typeof SessionMeta>

export default Meta
type Story = StoryObj<typeof Meta>

export const Default: Story = {
  render: (): JSX.Element => {
    const sessionDetail = {
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
        maxTokens: 1000
      },
      todos: [],
      turns: []
    }

    const onRefresh = async (): Promise<void> => {
      console.log('Refresh called')
      return Promise.resolve()
    }

    const onSessionDetailUpdate = (updatedDetail: typeof sessionDetail): void => {
      console.log('Session detail updated:', updatedDetail)
    }

    return (
      <div style={{ height: '600px', display: 'flex' }}>
        <SessionMeta
          sessionDetail={sessionDetail}
          onRefresh={onRefresh}
          onSessionDetailUpdate={onSessionDetailUpdate}
        />
      </div>
    )
  }
}

export const WithAriaAttributes: Story = {
  render: (): JSX.Element => {
    const sessionDetail = {
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

    const onRefresh = async (): Promise<void> => {
      // Simulate async refresh
      await new Promise((resolve) => setTimeout(resolve, 1000))
      console.log('Refresh completed')
    }

    return (
      <div style={{ height: '600px', display: 'flex' }}>
        <div style={{ flex: 1 }}>
          <SessionMeta
            sessionDetail={sessionDetail}
            onRefresh={onRefresh}
          />
        </div>
        <div style={{ padding: '16px', borderLeft: '1px solid #eee', width: '300px' }}>
          <h3>ARIA Features:</h3>
          <ul style={{ fontSize: '14px', lineHeight: '1.6' }}>
            <li>
              <strong>aria-label</strong>: Save button has descriptive label
              "Save session metadata"
            </li>
            <li>
              <strong>aria-busy</strong>: Indicates when save operation is in progress
            </li>
            <li>
              <strong>role="status"</strong>: Announces save success/failure to screen readers
            </li>
          </ul>
          <p style={{ fontSize: '12px', color: '#666', marginTop: '16px' }}>
            Try clicking the "Save Meta" button and observe the aria-busy state
            and status announcements.
          </p>
        </div>
      </div>
    )
  }
}
