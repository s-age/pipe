import { useCallback } from 'react'

import { editSessionMeta } from '@/lib/api/meta/editSessionMeta'
import type { EditSessionMetaRequest } from '@/lib/api/meta/editSessionMeta'
import { addToast } from '@/stores/useToastStore'

export const useSessionMetaActions = (): {
  handleMetaSave: (id: string, meta: EditSessionMetaRequest) => Promise<void>
} => {
  const handleMetaSave = useCallback(
    async (id: string, meta: EditSessionMetaRequest): Promise<void> => {
      try {
        await editSessionMeta(id, meta)
        addToast({ status: 'success', title: 'Session metadata saved' })
      } catch (error: unknown) {
        addToast({
          status: 'failure',
          title: (error as Error).message || 'Failed to save session meta.'
        })
      }
    },
    []
  )

  return { handleMetaSave }
}
