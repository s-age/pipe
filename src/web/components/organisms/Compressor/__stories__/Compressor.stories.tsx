import type { Meta as StoryMeta, StoryObj } from '@storybook/react-vite'
import type { JSX } from 'react'

import type { SessionDetail } from '@/lib/api/session/getSession'
import { AppStoreProvider } from '@/stores/useAppStore'

import { Compressor } from '../index'

const mockSessionDetail: SessionDetail = {
  artifacts: [],
  background: 'This is a test background for the compressor component.',
  hyperparameters: {
    temperature: 0.7,
    topP: 0.9,
    topK: 40
  },
  instruction: 'Please compress the following turns.',
  multiStepReasoningEnabled: true,
  parent: null,
  procedure: null,
  purpose: 'Testing the Compressor component rendering and behavior.',
  references: [],
  roles: ['developer'],
  sessionId: 'session-123',
  todos: [],
  turns: [
    {
      type: 'user_task',
      instruction: 'First user instruction',
      timestamp: '2024-01-01T10:00:00Z'
    },
    {
      type: 'model_response',
      content: 'First model response content.',
      timestamp: '2024-01-01T10:01:00Z'
    },
    {
      type: 'user_task',
      instruction: 'Second user instruction',
      timestamp: '2024-01-01T10:02:00Z'
    },
    {
      type: 'model_response',
      content: 'Second model response content.',
      timestamp: '2024-01-01T10:03:00Z'
    }
  ]
}

const Meta = {
  title: 'Organisms/Compressor',
  component: Compressor,
  tags: ['autodocs'],
  decorators: [
    (Story): JSX.Element => (
      <AppStoreProvider>
        <Story />
      </AppStoreProvider>
    )
  ],
  args: {
    onRefresh: async (): Promise<void> => {
      console.log('onRefresh called')
    }
  }
} satisfies StoryMeta<typeof Compressor>

export default Meta
type Story = StoryObj<typeof Meta>

export const Default: Story = {
  args: {
    sessionDetail: mockSessionDetail
  }
}

export const EmptyTurns: Story = {
  args: {
    sessionDetail: {
      ...mockSessionDetail,
      turns: []
    }
  }
}

export const NullSession: Story = {
  args: {
    sessionDetail: null
  }
}

export const ManyTurns: Story = {
  args: {
    sessionDetail: {
      ...mockSessionDetail,
      turns: Array.from({ length: 10 }, (_, i) =>
        i % 2 === 0
          ? {
              type: 'user_task',
              instruction: `Instruction ${i}`,
              timestamp: new Date().toISOString()
            }
          : {
              type: 'model_response',
              content: `Response ${i}`,
              timestamp: new Date().toISOString()
            }
      )
    }
  }
}

export const LongBackground: Story = {
  args: {
    sessionDetail: {
      ...mockSessionDetail,
      background: 'A very long background text '.repeat(20)
    }
  }
}
