import { useEffect, useRef } from 'react'

export const useInitialLoading = (loadFunction: () => Promise<void>): void => {
  const initializedReference = useRef(false)

  useEffect(() => {
    if (initializedReference.current) {
      return
    }
    initializedReference.current = true
    void loadFunction()
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])
}