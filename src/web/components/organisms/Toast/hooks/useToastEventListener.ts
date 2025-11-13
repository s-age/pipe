import { useEffect } from 'react'

import { onToastEvent } from '@/lib/toastEvents'
import type { ToastEventData } from '@/lib/toastEvents'
import { useAppStore } from '@/stores/useAppStore'

export const useToastEventListener = (): void => {
  const { pushToast } = useAppStore()

  useEffect(() => {
    const unsubscribe = onToastEvent((data: ToastEventData) => {
      pushToast(data)
    })

    return unsubscribe
  }, [pushToast])
}
