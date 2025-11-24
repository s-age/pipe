import { useEffect, useRef } from 'react'

type UseInstructionFormLifecycleProperties = {
  isStreaming: boolean
}

export const useInstructionFormLifecycle = ({
  isStreaming
}: UseInstructionFormLifecycleProperties): void => {
  const previousStreamingState = useRef<boolean>(isStreaming)

  // Focus on initial mount
  useEffect(() => {
    setTimeout(() => {
      const textarea = document.getElementById(
        'new-instruction-text'
      ) as HTMLTextAreaElement | null
      if (textarea) {
        textarea.focus()
      }
    }, 0)
  }, [])

  // Focus when streaming completes
  useEffect(() => {
    if (previousStreamingState.current && !isStreaming) {
      // Streaming just finished
      setTimeout(() => {
        const textarea = document.getElementById(
          'new-instruction-text'
        ) as HTMLTextAreaElement | null
        if (textarea) {
          textarea.focus()
        }
      }, 0)
    }
    previousStreamingState.current = isStreaming
  }, [isStreaming])
}
