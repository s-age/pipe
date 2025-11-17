import { useCallback } from 'react'
import type React from 'react'

import type { SessionDetail } from '@/lib/api/session/getSession'

import { useSessionItemActions } from './useSessionItemActions'

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
  const { loadSession } = useSessionItemActions()

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
      window.history.replaceState({}, '', `/session/${sessionId}`)
    },
    [loadSession, selectSession]
  )

  return { handleNewChatClick, setSessionReference, handleAnchorClick }
}
