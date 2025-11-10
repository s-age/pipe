import type { JSX } from 'react'

import { Heading } from '@/components/atoms/Heading'
import { TurnComponent as Turn } from '@/components/molecules/Turn'
import type { Turn as TurnType, SessionDetail } from '@/lib/api/session/getSession'

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
}

export const ChatHistoryBody = ({
  sessionDetail,
  currentSessionId,
  expertMode,
  isStreaming,
  streamedText,
  turnsListReference,
  onRefresh
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
        {((): JSX.Element[] => {
          const nodes: JSX.Element[] = []
          for (let i = 0; i < sessionDetail.turns.length; i += 1) {
            const turn: TurnType = sessionDetail.turns[i]
            nodes.push(
              <Turn
                key={i}
                turn={turn}
                index={i}
                sessionId={currentSessionId}
                expertMode={expertMode}
                onRefresh={onRefresh}
              />
            )
          }

          return nodes
        })()}
        {isStreaming && streamedText && (
          <Turn
            key="streaming-response"
            turn={{
              type: 'model_response',
              content: streamedText,
              timestamp: new Date().toISOString()
            }}
            index={sessionDetail.turns.length}
            sessionId={currentSessionId}
            expertMode={expertMode}
            onRefresh={onRefresh}
            isStreaming={isStreaming}
          />
        )}
      </section>
    </div>
  )
}
