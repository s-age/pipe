import { useToast } from '@/components/organisms/Toast/hooks/useToast'
import type { EditSessionMetaRequest } from '@/lib/api/session/editSessionMeta'
import { editSessionMeta } from '@/lib/api/session/editSessionMeta'

type UseSessionMetaSaverProperties = {
  onRefresh: () => Promise<void>
}

export const useSessionMetaSaver = ({
  onRefresh
}: UseSessionMetaSaverProperties): {
  handleMetaSave: (id: string, meta: EditSessionMetaRequest) => Promise<void>
} => {
  const toast = useToast()

  const handleMetaSave = async (
    id: string,
    meta: EditSessionMetaRequest
  ): Promise<void> => {
    try {
      await editSessionMeta(id, meta)
      await onRefresh()
      toast.success('Session metadata saved')
    } catch (error: unknown) {
      const message = (error as Error).message || 'Failed to save session meta.'
      toast.failure(message)
    }
  }

  return { handleMetaSave }
}
