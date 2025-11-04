import { useCallback } from 'react'

export const useSessionListHandlers = (): {
  handleNewChatClick: () => void
} => {
  const handleNewChatClick = useCallback(() => {
    window.location.href = '/start_session'
  }, [])

  return { handleNewChatClick }
}
