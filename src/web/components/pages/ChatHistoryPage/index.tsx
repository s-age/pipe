import type { JSX } from 'react'

import { AppLayout } from '@/components/layouts/AppLayout'
import { Flex } from '@/components/molecules/Flex'
import { FlexColumn } from '@/components/molecules/FlexColumn'
import { Navigation } from '@/components/molecules/Navigation'
import { ChatHistory } from '@/components/organisms/ChatHistory'
import { SessionControl } from '@/components/organisms/SessionControl'
import { SessionTree } from '@/components/organisms/SessionTree'

import { useChatHistoryPageHandlers } from './hooks/useChatHistoryPageHandlers'
import { mainContent, leftColumn, centerColumn } from './style.css.ts'

export const ChatHistoryPage = (): JSX.Element => {
  const {
    expertMode,
    handleSelectSession,
    onRefresh,
    refreshSessionsInStore,
    sessionDetail,
    sessions,
    setSessionDetail
  } = useChatHistoryPageHandlers()

  return (
    <AppLayout>
      <Flex className={mainContent}>
        <Navigation className={leftColumn} ariaLabel="Session navigation">
          <SessionTree
            currentSessionId={sessionDetail?.sessionId ?? null}
            sessions={sessions}
            handleSelectSession={handleSelectSession}
            onRefresh={onRefresh}
          />
        </Navigation>

        <FlexColumn className={centerColumn}>
          <ChatHistory
            sessionDetail={sessionDetail}
            expertMode={expertMode}
            setSessionDetail={setSessionDetail}
            refreshSessionsInStore={refreshSessionsInStore}
          />
        </FlexColumn>

        {sessionDetail && (
          <SessionControl
            sessionDetail={sessionDetail}
            onRefresh={onRefresh}
            onSessionDetailUpdate={setSessionDetail}
          />
        )}
      </Flex>
    </AppLayout>
  )
}
