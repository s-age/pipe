import { useCallback, useState } from 'react'

export type SessionControlTab = 'meta' | 'compress' | 'therapist'

export const useSessionControlHandlers = (
  initial: SessionControlTab = 'meta'
): { active: SessionControlTab; handleTabChange: (key: SessionControlTab) => void } => {
  const [active, setActive] = useState<SessionControlTab>(initial)

  const handleTabChange = useCallback((key: SessionControlTab): void => {
    setActive(key)
  }, [])

  return { active, handleTabChange }
}
