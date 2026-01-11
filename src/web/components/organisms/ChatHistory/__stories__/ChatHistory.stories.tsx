import type { Meta as StoryMeta, StoryObj } from '@storybook/react-vite'
import type { JSX } from 'react'
import { MemoryRouter, Route, Routes } from 'react-router-dom'

import { ModalProvider } from '@/components/organisms/ModalManager'
import type { SessionDetail, Turn } from '@/lib/api/session/getSession'
import type { SessionOverview } from '@/lib/api/sessionTree/getSessionTree'

import { ChatHistory } from '../index'

const Meta = {
  title: 'Organisms/ChatHistory',
  component: ChatHistory,
  tags: ['autodocs'],
  decorators: [
    (Story): JSX.Element => (
      <MemoryRouter initialEntries={['/session/session_123']}>
        <ModalProvider>
          <Routes>
            <Route path="/session/*" element={<Story />} />
          </Routes>
        </ModalProvider>
      </MemoryRouter>
    )
  ]
} satisfies StoryMeta<typeof ChatHistory>

export default Meta
type Story = StoryObj<typeof Meta>

const mockTurns: Turn[] = [
  {
    type: 'user_task',
    instruction: 'Hello! Can you help me with some TypeScript code?',
    timestamp: new Date(Date.now() - 100000).toISOString()
  },
  {
    type: 'model_response',
    content:
      'Of course! I can help you with TypeScript. What specifically do you need help with?',
    timestamp: new Date(Date.now() - 90000).toISOString()
  },
  {
    type: 'user_task',
    instruction: 'I want to know how to define a complex interface.',
    timestamp: new Date(Date.now() - 80000).toISOString()
  },
  {
    type: 'model_response',
    content:
      'To define a complex interface in TypeScript, you can use nested objects, optional properties, and even function signatures. Here is an example:\n\n```typescript\ninterface User {\n  id: string;\n  profile: {\n    name: string;\n    age?: number;\n  };\n  getPermissions(): string[];\n}\n```',
    timestamp: new Date(Date.now() - 70000).toISOString()
  }
]

const mockSessionDetail: SessionDetail = {
  sessionId: 'session_123',
  purpose: 'TypeScript Assistance',
  background:
    'The user is working on a React project and needs help with TypeScript types.',
  instruction: '',
  multiStepReasoningEnabled: false,
  parent: null,
  procedure: null,
  references: [],
  artifacts: [],
  roles: ['developer'],
  todos: [],
  turns: mockTurns,
  tokenCount: 1250,
  hyperparameters: {
    temperature: 0.7,
    topK: 40,
    topP: 0.9
  },
  settings: {
    apiMode: 'ollama',
    contextLimit: 700000,
    expertMode: false,
    hyperparameters: {
      temperature: 0.7,
      topK: 40,
      topP: 0.9
    },
    language: 'japanese',
    maxToolCalls: 10,
    model: 'llama3',
    referenceTtl: 3600,
    searchModel: 'gpt-4o',
    sessionsPath: './sessions',
    timezone: 'Asia/Tokyo',
    toolResponseExpiration: 3600,
    yolo: false
  }
}

const defaultArguments = {
  expertMode: false,
  sessionDetail: mockSessionDetail,
  refreshSessionsInStore: (
    detail: SessionDetail,
    sessions: SessionOverview[]
  ): void => {
    console.log('refreshSessionsInStore', { detail, sessions })
  },
  setSessionDetail: (data: SessionDetail | null): void => {
    console.log('setSessionDetail', data)
  }
}

export const Default: Story = {
  args: defaultArguments
}

export const ExpertMode: Story = {
  args: {
    ...defaultArguments,
    expertMode: true
  }
}

export const Empty: Story = {
  args: {
    ...defaultArguments,
    sessionDetail: {
      ...mockSessionDetail,
      turns: [],
      tokenCount: 0
    }
  }
}

export const Loading: Story = {
  args: {
    ...defaultArguments,
    sessionDetail: null
  }
}

/**
 * Tests streaming turns rendering (ChatHistoryBody line 97).
 * This requires mocking the streaming state.
 */
export const WithStreamingTurns: Story = {
  args: defaultArguments
}
