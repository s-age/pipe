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

      if (typeof session.session_id !== 'string') {
        // Actions hook will handle toast for invalid session ID
        return
      }

      const sessionDetail = await loadSession(session.session_id)
      selectSession(session.session_id, sessionDetail)
      navigate(`/session/${session.session_id}`, { replace: true })
    },
    [selectSession, session.session_id, loadSession, navigate]
  )

  return { onClick }
}
