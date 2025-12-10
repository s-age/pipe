import { editSessionMeta } from '@/lib/api/meta/editSessionMeta'
import type { EditSessionMetaRequest } from '@/lib/api/meta/editSessionMeta'
import { addToast } from '@/stores/useToastStore'

type UseSessionMetaActionsProperties = {
  onRefresh: () => Promise<void>
}

export const useSessionMetaActions = ({
  onRefresh
}: UseSessionMetaActionsProperties): {
  handleMetaSave: (id: string, meta: EditSessionMetaRequest) => Promise<void>
} => {
  const handleMetaSave = async (
    id: string,
    meta: EditSessionMetaRequest
  ): Promise<void> => {
    try {
      await editSessionMeta(id, meta)
      addToast({ status: 'success', title: 'Session metadata saved' })
      await onRefresh()
    } catch (error: unknown) {
      addToast({
        status: 'failure',
        title: (error as Error).message || 'Failed to save session meta.'
      })
    }
  }

  return { handleMetaSave }
}
