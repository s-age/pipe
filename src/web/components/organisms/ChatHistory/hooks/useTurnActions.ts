import { useCallback } from 'react'

import { useToast } from '@/components/organisms/Toast/hooks/useToast'
import { deleteSession } from '@/lib/api/session/deleteSession'
import { deleteTurn } from '@/lib/api/session/deleteTurn'
import { forkSession } from '@/lib/api/session/forkSession'

export const useTurnActions = (
  refreshSessions: () => Promise<void>,
): {
  handleDeleteTurn: (sessionId: string, turnIndex: number) => Promise<void>
  handleForkSession: (sessionId: string, forkIndex: number) => Promise<void>
  handleDeleteSession: (sessionId: string) => Promise<void>
} => {
  const toast = useToast()
  const handleDeleteTurn = useCallback(
    async (sessionId: string, turnIndex: number): Promise<void> => {
      if (!window.confirm('Are you sure you want to delete this turn?')) return
      try {
        await deleteTurn(sessionId, turnIndex)
        await refreshSessions()
      } catch (error: unknown) {
        toast.failure((error as Error).message || 'Failed to delete turn.')
      }
    },
    [refreshSessions, toast],
  )

  const handleForkSession = useCallback(
    async (sessionId: string, forkIndex: number): Promise<void> => {
      if (
        !window.confirm(
          `Are you sure you want to fork this session at turn index ${forkIndex + 1}?`,
        )
      )
        return

      try {
        const result = await forkSession(sessionId, forkIndex)
        if (result.new_session_id) {
          window.location.href = `/session/${result.new_session_id}`
        } else {
          throw new Error('Failed to fork session.')
        }
      } catch (error: unknown) {
        toast.failure((error as Error).message || 'Failed to fork session.')
      }
    },
    [toast],
  )

  const handleDeleteSession = useCallback(
    async (sessionId: string): Promise<void> => {
      if (!window.confirm('Are you sure you want to delete this session?')) return
      try {
        await deleteSession(sessionId)
        // const fetchedSessions = await getSessions()
        // setSessions(fetchedSessions.sessions.map(([, session]) => session))
        // setCurrentSessionId(null)
        // setSessionDetail(null)
        window.history.pushState({}, '', '/')
      } catch (error: unknown) {
        toast.failure((error as Error).message || 'Failed to delete session.')
      }
    },
    [toast],
  )

  return { handleDeleteTurn, handleForkSession, handleDeleteSession }
}
