import React from 'react'

import type { SessionDetail, Turn } from '@/lib/api/session/getSession'
import { AppStoreProvider } from '@/stores/useAppStore'

import { CompressorApproval } from '../CompressorApproval'
import { Compressor } from '../index'

const Wrapper = ({
  children
}: React.PropsWithChildren<unknown>): React.ReactElement => (
  <AppStoreProvider>{children}</AppStoreProvider>
)

const mockSummary =
  'This is a mock summary for testing purposes. It contains approximately 1000 characters to simulate a real compression summary. The original conversation involved multiple turns discussing various topics related to software development, including React components, TypeScript integration, and best practices for building scalable web applications. The participants explored different approaches to state management, component composition, and performance optimization techniques. They discussed the benefits of using hooks versus class components, the importance of proper typing in TypeScript, and how to structure large-scale applications for maintainability. Various code examples were shared, demonstrating patterns for handling asynchronous operations, managing side effects, and implementing responsive user interfaces. The conversation also touched on testing strategies, including unit testing, integration testing, and end-to-end testing methodologies. Participants exchanged ideas about CI/CD pipelines, deployment strategies, and monitoring tools for production applications. They debated the merits of different frontend frameworks and libraries, comparing features, performance characteristics, and community support. The discussion included topics like accessibility, internationalization, and security considerations in modern web development. Code review practices, pair programming techniques, and collaborative development workflows were also covered. The group explored emerging technologies and trends in the JavaScript ecosystem, including new language features, build tools, and development environments. They shared experiences with different project structures, from monorepos to micro-frontends, and discussed the trade-offs involved. Performance optimization was a recurring theme, with discussions about lazy loading, code splitting, memoization, and other techniques to improve application speed and user experience. The conversation highlighted the importance of developer experience, with talks about tooling, IDE support, and development workflows that enhance productivity. Security best practices were emphasized, including input validation, authentication mechanisms, and protection against common web vulnerabilities. The participants also discussed career development, learning resources, and staying updated with rapidly evolving technologies in the field.'

const createMockSessionDetail = (
  sessionId: string,
  turnCount: number
): SessionDetail => ({
  sessionId: sessionId,
  purpose: 'Test session for compression',
  background: 'Mock background',
  roles: ['user', 'assistant'],
  parent: null,
  references: [],
  artifacts: [],
  procedure: null,
  instruction: 'Test instruction',
  multiStepReasoningEnabled: false,
  hyperparameters: null,
  todos: [],
  turns: Array.from({ length: turnCount }, (_, i) => ({
    type: i % 2 === 0 ? 'user_task' : 'model_response',
    content: `Turn ${i} content`,
    instruction: `Turn ${i} instruction`,
    timestamp: new Date().toISOString(),
    response: { status: 'success' }
  })) as unknown as Turn[]
})

export default {
  title: 'Components/Compressor',
  component: Compressor,
  parameters: {
    layout: 'centered'
  },
  argTypes: {
    sessionDetail: {
      control: 'object',
      description: 'Session detail object'
    }
  },
  decorators: [
    (Story: () => React.ReactElement): React.ReactElement => (
      <Wrapper>
        <Story />
      </Wrapper>
    )
  ]
}

export const Default = (): React.ReactElement => (
  <div style={{ padding: 16 }}>
    <Compressor
      sessionDetail={createMockSessionDetail('session_abc123', 8)}
      onRefresh={async () => {}}
    />
  </div>
)

export const WithManyTurns = (): React.ReactElement => (
  <div style={{ padding: 16 }}>
    <Compressor
      sessionDetail={createMockSessionDetail('session_xyz789', 50)}
      onRefresh={async () => {}}
    />
  </div>
)

export const WithFewTurns = (): React.ReactElement => (
  <div style={{ padding: 16 }}>
    <Compressor
      sessionDetail={createMockSessionDetail('session_minimal', 3)}
      onRefresh={async () => {}}
    />
  </div>
)

export const ApprovalStage = (): React.ReactElement => {
  const [summary, setSummary] = React.useState(mockSummary)
  const [, setError] = React.useState<string | null>(null)
  const [isSubmitting, setIsSubmitting] = React.useState(false)
  const [, setCompressorSessionId] = React.useState<string | null>('mock-compressor-id')

  const handleDeny = (): void => {
    setSummary('')
    setError(null)
    setCompressorSessionId(null)
  }

  return (
    <div style={{ padding: 16 }}>
      <CompressorApproval
        summary={summary}
        sessionId="mock-session-id"
        setSummary={setSummary}
        setError={setError}
        setIsSubmitting={setIsSubmitting}
        handleDeny={handleDeny}
        isSubmitting={isSubmitting}
        compressorSessionId="mock-compressor-id"
        setCompressorSessionId={() => {}}
        onRefresh={async () => {}}
      />
    </div>
  )
}
