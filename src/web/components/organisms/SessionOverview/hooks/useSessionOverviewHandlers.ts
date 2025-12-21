import { useCallback } from 'react'
import { useNavigate } from 'react-router-dom'

import type { SessionOverview } from '@/lib/api/sessionTree/getSessionTree'

export const useSessionOverviewHandlers = ({
  session,
  handleSelectSession
}: {
  session: SessionOverview
  handleSelectSession: (sessionId: string) => Promise<void>
}): {
  onClick: (event: React.MouseEvent<HTMLAnchorElement>) => Promise<void>
} => {
  const navigate = useNavigate()

  const onClick = useCallback(
    async (event: React.MouseEvent<HTMLAnchorElement>): Promise<void> => {
      event.preventDefault()

      if (typeof session.sessionId !== 'string') {
        return
      }

      // Navigate first, then refresh metadata
      navigate(`/session/${session.sessionId}`, { replace: true })
      await handleSelectSession(session.sessionId)
    },
    [handleSelectSession, session.sessionId, navigate]
  )

  return { onClick }
}
