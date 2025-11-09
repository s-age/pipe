import { useCallback } from 'react'

import { getSession } from '@/lib/api/session/getSession'
import type { SessionDetail } from '@/lib/api/session/getSession'
import type { SessionOverview } from '@/lib/api/sessionTree/getSessionTree'

export const useSessionItemHandlers = ({
  session,
  selectSession,
  setError,
}: {
  session: SessionOverview
  selectSession: (id: string | null, detail: SessionDetail | null) => void
  setError: (message: string | null) => void
}): {
  onClick: (event: React.MouseEvent<HTMLAnchorElement>) => Promise<void>
} => {
  const onClick = useCallback(
    async (event: React.MouseEvent<HTMLAnchorElement>): Promise<void> => {
      event.preventDefault()

      if (typeof session.session_id !== 'string') {
        setError('Invalid session ID.')

        return
      }

      try {
        const sessionDetail = await getSession(session.session_id)
        selectSession(session.session_id, sessionDetail.session)
        window.history.replaceState({}, '', `/session/${session.session_id}`)
      } catch (error) {
        setError((error as Error).message || 'Failed to load session data.')
      }
    },
    [selectSession, session.session_id, setError],
  )

  return { onClick }
}

// Default export removed — use named export `useSessionItemHandlers`
