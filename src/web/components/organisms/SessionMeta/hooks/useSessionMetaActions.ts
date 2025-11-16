import { editSessionMeta } from '@/lib/api/session/editSessionMeta'
import type { EditSessionMetaRequest } from '@/lib/api/session/editSessionMeta'
import { emitToast } from '@/lib/toastEvents'

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
      emitToast.success('Session metadata saved')
      await onRefresh()
    } catch (error: unknown) {
      emitToast.failure((error as Error).message || 'Failed to save session meta.')
    }
  }

  return { handleMetaSave }
}
