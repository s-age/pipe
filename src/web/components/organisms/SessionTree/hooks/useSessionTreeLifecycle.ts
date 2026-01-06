import { useEffect, useRef } from 'react'

type UseSessionTreeLifecycleProperties = {
  currentSessionId: string | null
  sessionReferences: React.MutableRefObject<Map<string, HTMLLIElement>>
  sessions: Array<{ sessionId: string }>
}

export const useSessionTreeLifecycle = ({
  currentSessionId,
  sessionReferences,
  sessions
}: UseSessionTreeLifecycleProperties): void => {
  const hasScrolled = useRef(false)

  // Scroll to selected session on initial load and when currentSessionId changes
  useEffect(() => {
    if (currentSessionId && sessions.length > 0) {
      const element = sessionReferences.current.get(currentSessionId)
      if (element) {
        // Add a small delay to ensure DOM is ready
        setTimeout(() => {
          element.scrollIntoView({
            behavior: hasScrolled.current ? 'smooth' : 'auto',
            block: 'center'
          })
          hasScrolled.current = true
        }, 100)
      }
    }
  }, [currentSessionId, sessions.length, sessionReferences])
}
