import { useState } from 'react'

import type { Turn } from '@/lib/api/session/getSession'

type UseTurnLifecycleProperties = {
  turn: Turn
}

export const useTurnLifecycle = ({
  turn
}: UseTurnLifecycleProperties): {
  isEditing: boolean
  editedContent: string
  setIsEditing: (isEditing: boolean) => void
  setEditedContent: (editedContent: string) => void
} => {
  const [isEditing, setIsEditing] = useState<boolean>(false)
  const [editedContent, setEditedContent] = useState<string>(
    turn.content ?? turn.instruction ?? ''
  )

  return {
    isEditing,
    editedContent,
    setIsEditing,
    setEditedContent
  }
}
