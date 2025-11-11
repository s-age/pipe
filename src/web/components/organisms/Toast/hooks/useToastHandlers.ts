import { useMemo } from 'react'

import { useAppStore } from '@/stores/useAppStore'
import type { ToastItem as ToastItemType } from '@/stores/useAppStore'

const allPositions = [
  'top-left',
  'top-center',
  'top-right',
  'bottom-left',
  'bottom-center',
  'bottom-right'
] as const

export const useToastHandlers = (): {
  grouped: Record<string, ToastItemType[]>
} => {
  const { state } = useAppStore()

  const grouped = useMemo<Record<string, ToastItemType[]>>(() => {
    const map: Record<string, ToastItemType[]> = {}
    for (const p of allPositions) map[p] = []
    for (const t of state.toasts) {
      const pos = (t.position as string) ?? 'top-right'
      if (!map[pos]) map[pos] = []
      map[pos].push(t as ToastItemType)
    }

    return map
  }, [state.toasts])

  return { grouped }
}
