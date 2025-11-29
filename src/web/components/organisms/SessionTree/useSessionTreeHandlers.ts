import { useCallback } from 'react'
import type React from 'react'
import { useNavigate } from 'react-router-dom'

import type { SessionDetail } from '@/lib/api/session/getSession'

import { useSessionOverviewActions } from '../SessionOverview/hooks/useSessionOverviewActions'

type UseSessionTreeHandlersReturn = {
  handleNewChatClick: () => void
  setSessionReference: (sessionId: string) => (element: HTMLLIElement | null) => void
  handleAnchorClick: (event: React.MouseEvent<HTMLAnchorElement>) => Promise<void>
}

// `selectSession` is provided by the page to update selected session in the store.
export const useSessionTreeHandlers = (
  selectSession: (id: string | null, detail: SessionDetail | null) => void,
  sessionReferences: React.RefObject<Map<string, HTMLLIElement>>
): UseSessionTreeHandlersReturn => {
  const { loadSession } = useSessionOverviewActions()
  const navigate = useNavigate()

  const handleNewChatClick = useCallback(() => {
    window.location.href = '/start_session'
  }, [])

  const setSessionReference = useCallback(
    (sessionId: string) =>
      (element: HTMLLIElement | null): void => {
        if (!sessionReferences) return

        if (element) {
          sessionReferences.current.set(sessionId, element)
        } else {
          sessionReferences.current.delete(sessionId)
        }
      },
    [sessionReferences]
  )

  const handleAnchorClick = useCallback(
    async (event: React.MouseEvent<HTMLAnchorElement>): Promise<void> => {
      event.preventDefault()
      const sessionId = event.currentTarget.getAttribute('data-session-id')
      if (!sessionId) return

      const sessionDetail = await loadSession(sessionId)
      selectSession(sessionId, sessionDetail)
      navigate(`/session/${sessionId}`, { replace: true })
    },
    [loadSession, selectSession, navigate]
  )

  return { handleNewChatClick, setSessionReference, handleAnchorClick }
}
