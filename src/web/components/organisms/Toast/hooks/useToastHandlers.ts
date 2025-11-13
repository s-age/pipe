import { useMemo } from 'react'

import type { ToastItem } from './useToastEventListener'

const allPositions = [
  'top-left',
  'top-center',
  'top-right',
  'bottom-left',
  'bottom-center',
  'bottom-right'
] as const

export const useToastHandlers = (
  toasts: ToastItem[]
): {
  grouped: Record<string, ToastItem[]>
} => {
  const grouped = useMemo<Record<string, ToastItem[]>>(() => {
    const map: Record<string, ToastItem[]> = {}
    for (const p of allPositions) map[p] = []
    for (const t of toasts) {
      const pos = (t.position as string) ?? 'top-right'
      if (!map[pos]) map[pos] = []
      map[pos].push(t)
    }

    return map
  }, [toasts])

  return { grouped }
}
