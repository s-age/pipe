import { useCallback } from 'react'
import { useNavigate } from 'react-router-dom'

import type { SessionDetail } from '@/lib/api/session/getSession'
import type { SessionOverview } from '@/lib/api/sessionTree/getSessionTree'

import { useSessionItemActions } from './useSessionItemActions'

export const useSessionItemHandlers = ({
  session,
  selectSession
}: {
  session: SessionOverview
  selectSession: (id: string | null, detail: SessionDetail | null) => void
}): {
  onClick: (event: React.MouseEvent<HTMLAnchorElement>) => Promise<void>
} => {
  const { loadSession } = useSessionItemActions()
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
      navigate(`/session/${session.sessionId}`, { replace: true })
    },
    [selectSession, session.sessionId, loadSession, navigate]
  )

  return { onClick }
}
