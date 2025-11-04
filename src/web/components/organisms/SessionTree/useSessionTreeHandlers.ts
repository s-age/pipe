import { useCallback } from 'react'

export const useSessionTreeHandlers = (): {
  handleNewChatClick: () => void
} => {
  const handleNewChatClick = useCallback(() => {
    window.location.href = '/start_session'
  }, [])

  return { handleNewChatClick }
}
