import { useEffect, useMemo, useRef } from 'react'

type UseInstructionFormLifecycleProperties = {
  isStreaming: boolean
  tokenCount: number
  contextLimit: number
}

type ContextLeftInfo = {
  contextLeft: string
  colorKey: 'cyan' | 'orange' | 'red'
}

export const useInstructionFormLifecycle = ({
  isStreaming,
  tokenCount,
  contextLimit
}: UseInstructionFormLifecycleProperties): ContextLeftInfo => {
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

  // Calculate context left info
  const contextLeftInfo = useMemo(() => {
    const contextLeft = (100 - Math.floor((tokenCount / contextLimit) * 100)).toFixed(0)
    const contextLeftPercent = parseInt(contextLeft)
    const colorKey: 'cyan' | 'orange' | 'red' =
      contextLeftPercent >= 80 ? 'cyan' : contextLeftPercent >= 50 ? 'orange' : 'red'

    return { contextLeft, colorKey }
  }, [tokenCount, contextLimit])

  return contextLeftInfo
}
