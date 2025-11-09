import { useState, useEffect, useRef, useMemo } from 'react'

type StreamingFetchOptions = {
  method?: string
  headers?: HeadersInit
  body?: BodyInit | null
}

export const useStreamingFetch = (
  url: string | null,
  options: StreamingFetchOptions = {},
  callbacks?: {
    onChunk?: (chunk: string) => void
    // onComplete receives (error, finalStreamedText)
    onComplete?: (error: string | null, finalStreamedText: string) => void
  }
): {
  streamedText: string
  isLoading: boolean
  error: string | null
  setStreamedText: React.Dispatch<React.SetStateAction<string>>
} => {
  const [streamedText, setStreamedText] = useState<string>('')
  const [isLoading, setIsLoading] = useState<boolean>(false)
  const [error, setError] = useState<string | null>(null)
  const controllerReference = useRef<AbortController | null>(null)

  // optionsが安定していることを保証するために useMemo を使用
  const stableOptions = useMemo((): StreamingFetchOptions => options, [options])

  useEffect((): (() => void) => {
    if (!url) {
      setStreamedText('')
      if (controllerReference.current) {
        controllerReference.current.abort()
      }

      return (): void => {}
    }

    // 新しいリクエストが開始される前に古いコントローラをクリーンアップ
    if (controllerReference.current) {
      controllerReference.current.abort()
    }
    controllerReference.current = new AbortController()
    const signal = controllerReference.current.signal

    const fetchData = async (): Promise<void> => {
      setIsLoading(true)
      setError(null)
      setStreamedText('')
      let localError: string | null = null
      let accum = ''

      try {
        const response = await fetch(url, { ...stableOptions, signal })

        if (!response.ok) {
          const errorData = await response.json()
          throw new Error(errorData.message || `HTTP Error: ${response.status}`)
        }

        if (!response.body) {
          throw new Error('Response body is empty.')
        }

        const reader = response.body.getReader()
        const decoder = new TextDecoder()
        let done = false

        while (!done) {
          const { value, done: readerDone } = await reader.read()
          done = readerDone
          const chunk = decoder.decode(value, { stream: true })

          if (chunk) {
            accum += chunk
            setStreamedText((previous) => previous + chunk)
            // notify optional chunk callback
            try {
              callbacks?.onChunk?.(chunk)
            } catch (callbackError) {
              // swallow callback errors to not break the stream
              console.error('[useStreamingFetch] onChunk callback error', callbackError)
            }
          }
        }
      } catch (error_: unknown) {
        console.error('[ERROR] Failed to fetch stream:', error_)
        localError = (error_ as Error).message || 'Failed to fetch stream.'
        setError(localError)
      } finally {
        setIsLoading(false)
        // notify completion (pass error message or final streamed text)
        try {
          callbacks?.onComplete?.(localError, accum)
        } catch (onCompleteError) {
          console.error(
            '[useStreamingFetch] onComplete callback error',
            onCompleteError
          )
        }
      }
    }

    fetchData()

    return (): void => {
      if (controllerReference.current) {
        controllerReference.current.abort()
      }
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [url, stableOptions])

  return useMemo(
    (): {
      streamedText: string
      isLoading: boolean
      error: string | null
      setStreamedText: React.Dispatch<React.SetStateAction<string>>
    } => ({
      streamedText,
      isLoading,
      error,
      setStreamedText
    }),
    [streamedText, isLoading, error, setStreamedText]
  )
}
