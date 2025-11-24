import { useCallback } from 'react'

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

  const onClick = useCallback(
    async (event: React.MouseEvent<HTMLAnchorElement>): Promise<void> => {
      event.preventDefault()

      if (typeof session.session_id !== 'string') {
        // Actions hook will handle toast for invalid session ID
        return
      }

      const sessionDetail = await loadSession(session.session_id)
      selectSession(session.session_id, sessionDetail)
      window.history.replaceState({}, '', `/session/${session.session_id}`)
    },
    [selectSession, session.session_id, loadSession]
  )

  return { onClick }
}
