import { useEffect, useRef } from 'react'

type UseChatHistoryLifecycleProperties = {
  currentSessionId: string | null
  scrollToBottom: () => void
}

export const useChatHistoryLifecycle = ({
  currentSessionId,
  scrollToBottom
}: UseChatHistoryLifecycleProperties): void => {
  const previousSessionId = useRef<string | null>(null)

  // Scroll to bottom when session changes
  useEffect(() => {
    if (
      currentSessionId &&
      previousSessionId.current !== null &&
      previousSessionId.current !== currentSessionId
    ) {
      // Chain two requestAnimationFrame calls to ensure DOM is fully updated
      requestAnimationFrame(() => {
        requestAnimationFrame(() => {
          scrollToBottom()
        })
      })
    }
    previousSessionId.current = currentSessionId
  }, [currentSessionId, scrollToBottom])
}
