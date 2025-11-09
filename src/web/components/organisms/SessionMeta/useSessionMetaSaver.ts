import { useToast } from '@/components/organisms/Toast/hooks/useToast'
import type { EditSessionMetaRequest } from '@/lib/api/session/editSessionMeta'
import { editSessionMeta } from '@/lib/api/session/editSessionMeta'
import type { Actions } from '@/stores/useChatHistoryStore'

type UseSessionMetaSaverProperties = {
  actions: Actions
}

export const useSessionMetaSaver = ({
  actions
}: UseSessionMetaSaverProperties): {
  handleMetaSave: (id: string, meta: EditSessionMetaRequest) => Promise<void>
} => {
  const { refreshSessions } = actions
  const toast = useToast()

  const handleMetaSave = async (
    id: string,
    meta: EditSessionMetaRequest
  ): Promise<void> => {
    try {
      await editSessionMeta(id, meta)
      await refreshSessions()
      // show a transient toast
      toast.success('Session metadata saved')
    } catch (error: unknown) {
      const message = (error as Error).message || 'Failed to save session meta.'
      // use toast for user-visible error and clear persistent setError state
      toast.failure(message)
    }
  }

  return { handleMetaSave }
}
