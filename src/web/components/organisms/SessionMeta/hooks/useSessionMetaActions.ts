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
      await onRefresh()
      // show a transient toast
      emitToast.success('Session metadata saved')
    } catch (error: unknown) {
      const message = (error as Error).message || 'Failed to save session meta.'
      // use toast for user-visible error and clear persistent setError state
      emitToast.failure(message)
    }
  }

  return { handleMetaSave }
}
