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
  const [editedContent, setEditedContent] = useState<string>(() => {

    if (turn.content || turn.instruction) {
      return turn.content ?? turn.instruction ?? ''
    }
    if (turn.response) {
      if (typeof turn.response === 'string') {
        return turn.response
      }
      if (turn.response.message) {
        return typeof turn.response.message === 'string'
          ? turn.response.message
          : JSON.stringify(turn.response.message, null, 2)
      }

      return JSON.stringify(turn.response, null, 2)
    }

    return ''
  })

  return {
    isEditing,
    editedContent,
    setIsEditing,
    setEditedContent
  }
}
