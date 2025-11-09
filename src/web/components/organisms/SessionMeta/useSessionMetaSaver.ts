import type { EditSessionMetaRequest } from '@/lib/api/session/editSessionMeta'
import { editSessionMeta } from '@/lib/api/session/editSessionMeta'
import type { Actions } from '@/stores/useChatHistoryStore'

type UseSessionMetaSaverProperties = {
  actions: Actions
}

export const useSessionMetaSaver = ({
  actions,
}: UseSessionMetaSaverProperties): {
  handleMetaSave: (id: string, meta: EditSessionMetaRequest) => Promise<void>
} => {
  const { setError, refreshSessions } = actions

  const handleMetaSave = async (
    id: string,
    meta: EditSessionMetaRequest,
  ): Promise<void> => {
    try {
      await editSessionMeta(id, meta)
      await refreshSessions()
      setError(null)
    } catch (error: unknown) {
      setError((error as Error).message || 'Failed to save session meta.')
    }
  }

  return { handleMetaSave }
}
