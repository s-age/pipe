import {
  editSessionMeta,
  EditSessionMetaRequest,
} from '@/lib/api/session/editSessionMeta'
import { Actions } from '@/stores/useChatHistoryStore'

type UseSessionMetaSaverProps = {
  actions: Actions
}

export const useSessionMetaSaver = ({
  actions,
}: UseSessionMetaSaverProps): {
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
    } catch (err: unknown) {
      setError((err as Error).message || 'Failed to save session meta.')
    }
  }

  return { handleMetaSave }
}
