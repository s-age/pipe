import type { JSX } from 'react'

import { Heading } from '@/components/atoms/Heading'
import { TurnComponent as Turn } from '@/components/organisms/Turn'
import type { Turn as TurnType } from '@/lib/api/session/getSession'
import type { SessionDetail } from '@/lib/api/session/getSession'
import type { SessionOverview } from '@/lib/api/sessionTree/getSessionTree'

import { ChatHistoryTurn } from './ChatHistoryTurn'
import {
  turnsColumn,
  turnsListSection,
  welcomeMessage,
  panel,
  panelBottomSpacing
} from './style.css'

type ChatHistoryBodyProperties = {
  sessionDetail: SessionDetail | null
  currentSessionId: string | null
  expertMode: boolean
  isStreaming: boolean
  streamedText: string | null
  turnsListReference: React.RefObject<HTMLDivElement | null>
  onRefresh: () => Promise<void>
  refreshSessionsInStore: (
    sessionDetail: SessionDetail,
    sessions: SessionOverview[]
  ) => void
}

export const ChatHistoryBody = ({
  sessionDetail,
  currentSessionId,
  expertMode,
  isStreaming,
  streamedText,
  turnsListReference,
  onRefresh,
  refreshSessionsInStore
}: ChatHistoryBodyProperties): JSX.Element => {
  if (!currentSessionId || !sessionDetail) {
    return (
      <div className={turnsColumn}>
        <div className={welcomeMessage}>
          <Heading level={1}>Welcome</Heading>
          <p>Select a session from the sidebar to view its details.</p>
        </div>
      </div>
    )
  }

  return (
    <div className={`${panel} ${panelBottomSpacing}`}>
      <section className={turnsListSection} ref={turnsListReference}>
        {sessionDetail.turns.map((turn: TurnType, i: number) => {
          // Use a composite key that includes content/instruction to force remount on edit
          // Simple hash function to keep key reasonable length
          const content = turn.content ?? turn.instruction ?? ''
          const simpleHash = content
            .split('')
            .reduce(
              (accumulator, char) =>
                ((accumulator << 5) - accumulator + char.charCodeAt(0)) | 0,
              0
            )
          const key = `${turn.timestamp}-${i}-${simpleHash}`

          return (
            <ChatHistoryTurn
              key={key}
              turn={turn}
              index={i}
              currentSessionId={currentSessionId}
              expertMode={expertMode}
              onRefresh={onRefresh}
              refreshSessionsInStore={refreshSessionsInStore}
            />
          )
        })}
        {isStreaming && streamedText && (
          <Turn
            key="streaming-response"
            turn={{
              type: 'model_response',
              content: streamedText,
              timestamp: new Date().toISOString()
            }}
            index={sessionDetail.turns.length}
            expertMode={expertMode}
            isStreaming={isStreaming}
          />
        )}
      </section>
    </div>
  )
}
