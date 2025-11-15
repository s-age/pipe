import { editSessionMeta } from '@/lib/api/session/editSessionMeta'
import type { EditSessionMetaRequest } from '@/lib/api/session/editSessionMeta'

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
    await editSessionMeta(id, meta)
    await onRefresh()
  }

  return { handleMetaSave }
}
