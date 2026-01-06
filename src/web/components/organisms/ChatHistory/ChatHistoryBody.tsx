import { clsx } from 'clsx'
import type { JSX, RefObject } from 'react'

import { Heading } from '@/components/atoms/Heading'
import { TurnComponent as Turn } from '@/components/organisms/Turn'
import type { Turn as TurnType } from '@/lib/api/session/getSession'
import type { SessionDetail } from '@/lib/api/session/getSession'
import type { SessionOverview } from '@/lib/api/sessionTree/getSessionTree'

import { useChatHistoryLifecycle } from './hooks/useChatHistoryLifecycle'
import {
  turnsColumn,
  turnsListSection,
  welcomeMessage,
  panel,
  panelBottomSpacing
} from './style.css'

type ChatHistoryBodyProperties = {
  currentSessionId: string | null
  expertMode: boolean
  isStreaming: boolean
  sessionDetail: SessionDetail | null
  streamingTurns: TurnType[]
  turnsListReference: RefObject<HTMLDivElement | null>
  onRefresh: () => Promise<void>
  refreshSessionsInStore: (
    sessionDetail: SessionDetail,
    sessions: SessionOverview[]
  ) => void
  scrollToBottom: () => void
}

export const ChatHistoryBody = ({
  currentSessionId,
  expertMode,
  isStreaming,
  sessionDetail,
  streamingTurns,
  turnsListReference,
  onRefresh,
  refreshSessionsInStore,
  scrollToBottom
}: ChatHistoryBodyProperties): JSX.Element => {
  // Scroll to bottom when session changes
  useChatHistoryLifecycle({
    currentSessionId,
    scrollToBottom
  })

  if (!currentSessionId) {
    return (
      <div className={turnsColumn}>
        <div className={welcomeMessage}>
          <Heading level={1}>Welcome</Heading>
          <p>Select a session from the sidebar to view its details.</p>
        </div>
      </div>
    )
  }

  if (!sessionDetail) {
    return (
      <div className={turnsColumn}>
        <div className={welcomeMessage}>
          <Heading level={1}>Session Not Found</Heading>
          <p>
            The selected session could not be found. It may have been deleted or the ID
            is invalid.
          </p>
        </div>
      </div>
    )
  }

  return (
    <div className={clsx(panel, panelBottomSpacing)}>
      <section className={turnsListSection} ref={turnsListReference}>
        {sessionDetail.turns.map((turn: TurnType, i: number) => (
          <Turn
            key={i}
            turn={turn}
            index={i}
            expertMode={expertMode}
            sessionId={currentSessionId}
            onRefresh={onRefresh}
            refreshSessionsInStore={refreshSessionsInStore}
          />
        ))}

        {isStreaming &&
          streamingTurns.map((turn, turnIndex) => (
            <Turn
              key={`streaming-turn-${turnIndex}`}
              turn={turn}
              index={sessionDetail.turns.length + turnIndex}
              expertMode={expertMode}
              isStreaming={isStreaming}
            />
          ))}
      </section>
    </div>
  )
}
