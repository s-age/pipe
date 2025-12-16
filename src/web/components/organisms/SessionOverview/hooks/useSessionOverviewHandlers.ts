import { useCallback } from 'react'
import { useNavigate } from 'react-router-dom'

import type { SessionDetail } from '@/lib/api/session/getSession'
import type { SessionOverview } from '@/lib/api/sessionTree/getSessionTree'

import { useSessionOverviewActions } from './useSessionOverviewActions'

export const useSessionOverviewHandlers = ({
  session,
  selectSession
}: {
  session: SessionOverview
  selectSession: (id: string | null, detail: SessionDetail | null) => void
}): {
  onClick: (event: React.MouseEvent<HTMLAnchorElement>) => Promise<void>
} => {
  const { loadSession } = useSessionOverviewActions()
  const navigate = useNavigate()

  const onClick = useCallback(
    async (event: React.MouseEvent<HTMLAnchorElement>): Promise<void> => {
      event.preventDefault()

      if (typeof session.sessionId !== 'string') {
        // Actions hook will handle toast for invalid session ID
        return
      }

      const sessionDetail = await loadSession(session.sessionId)
      selectSession(session.sessionId, sessionDetail || null)
      // Use react-router navigation so router params update reliably.
      navigate(`/session/${session.sessionId}`, { replace: true })
    },
    [selectSession, session.sessionId, loadSession, navigate]
  )

  return { onClick }
}
