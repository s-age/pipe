import { useState, useEffect, useRef, useMemo } from 'react'

type StreamingFetchOptions = {
  method?: string
  headers?: HeadersInit
  body?: BodyInit
}

export const useStreamingFetch = (
  url: string | null,
  options: StreamingFetchOptions = {},
) => {
  const [streamedText, setStreamedText] = useState<string>('')
  const [isLoading, setIsLoading] = useState<boolean>(false)
  const [error, setError] = useState<string | null>(null)
  const controllerRef = useRef<AbortController | null>(null)

  // optionsが安定していることを保証するために useMemo を使用
  const stableOptions = useMemo(() => options, [options])

  useEffect(() => {
    if (!url) {
      setStreamedText('')
      if (controllerRef.current) {
        controllerRef.current.abort()
      }

      return
    }

    // 新しいリクエストが開始される前に古いコントローラをクリーンアップ
    if (controllerRef.current) {
      controllerRef.current.abort()
    }
    controllerRef.current = new AbortController()
    const signal = controllerRef.current.signal

    const fetchData = async () => {
      setIsLoading(true)
      setError(null)
      setStreamedText('')

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
            setStreamedText((prev) => prev + chunk)
          }
        }
      } catch (err: unknown) {
        console.error('[ERROR] Failed to fetch stream:', err)
        setError((err as Error).message || 'Failed to fetch stream.')
      } finally {
        setIsLoading(false)
      }
    }

    fetchData()

    return () => {
      if (controllerRef.current) {
        controllerRef.current.abort()
      }
    }
  }, [url, stableOptions])

  // 戻り値全体をuseMemoで安定化させる
  return useMemo(
    () => ({
      streamedText,
      isLoading,
      error,
      setStreamedText,
    }),
    [streamedText, isLoading, error, setStreamedText],
  )
}
