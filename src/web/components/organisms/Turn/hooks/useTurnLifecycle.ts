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
    if (turn.type === 'user_task') {
      return turn.instruction
    }
    if (turn.type === 'model_response' || turn.type === 'compressed_history') {
      return turn.content
    }
    if (turn.type === 'function_calling') {
      return turn.response
    }
    if (turn.type === 'tool_response') {
      if (typeof turn.response.message === 'string') {
        return turn.response.message
      }

      return JSON.stringify(turn.response.message, null, 2)
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
