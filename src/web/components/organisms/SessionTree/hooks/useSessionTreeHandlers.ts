import { useCallback, useRef } from 'react'
import type React from 'react'
import { useNavigate } from 'react-router-dom'

import type { SessionDetail } from '@/lib/api/session/getSession'

import { useSessionItemActions } from './useSessionItemActions'

type UseSessionTreeHandlersReturn = {
  sessionReferences: React.RefObject<Map<string, HTMLLIElement>>
  handleNewChatClick: () => void
  setSessionReference: (sessionId: string) => (element: HTMLLIElement | null) => void
  handleAnchorClick: (event: React.MouseEvent<HTMLAnchorElement>) => Promise<void>
}

// `selectSession` is provided by the page to update selected session in the store.
export const useSessionTreeHandlers = (
  selectSession: (id: string | null, detail: SessionDetail | null) => void,
  onRefresh: (sessionId?: string) => Promise<void>
): UseSessionTreeHandlersReturn => {
  const sessionReferences = useRef<Map<string, HTMLLIElement>>(new Map())
  const { loadSession } = useSessionItemActions()
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
      let sessionId = event.currentTarget.getAttribute('data-session-id')
      const href = event.currentTarget.getAttribute('href') || ''
      console.debug(
        '[SessionTree] handleAnchorClick data-session-id:',
        sessionId,
        'href:',
        href
      )

      // Fallback: if data attribute is missing or appears truncated (e.g. missing child segment),
      // derive ID from the href (`/session/<id>`). Prefer longer value assuming it is more specific.
      if (href.startsWith('/session/')) {
        const hrefId = href.substring('/session/'.length)
        if (!sessionId || hrefId.length > sessionId.length) {
          console.debug('[SessionTree] derived sessionId from href:', hrefId)
          sessionId = hrefId
        }
      }

      if (!sessionId) return

      const sessionDetail = await loadSession(sessionId)
      console.debug('[SessionTree] selectSession ->', sessionId)
      selectSession(sessionId, sessionDetail)
      // Use react-router navigation so router params update reliably.
      navigate(`/session/${sessionId}`, { replace: true })
      await onRefresh(sessionId)
    },
    [loadSession, selectSession, navigate, onRefresh]
  )

  return {
    sessionReferences,
    handleNewChatClick,
    setSessionReference,
    handleAnchorClick
  }
}
