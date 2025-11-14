import { useCallback } from 'react'

import { editHyperparameters } from '@/lib/api/session/editHyperparameters'
import type { EditHyperparametersRequest } from '@/lib/api/session/editHyperparameters'
import type { SessionDetail } from '@/lib/api/session/getSession'
import { emitToast } from '@/lib/toastEvents'

export const useHyperParametersActions = (): {
  updateHyperparameters: (
    sessionId: string,
    payload: EditHyperparametersRequest
  ) => Promise<{ message: string; session: SessionDetail }>
} => {
  const updateHyperparameters = useCallback(
    async (sessionId: string, payload: EditHyperparametersRequest) => {
      try {
        const result = await editHyperparameters(sessionId, payload)
        emitToast.success(result?.message || 'Hyperparameters updated')

        return result
      } catch (error: unknown) {
        emitToast.failure(
          (error as Error).message || 'Failed to update hyperparameters'
        )
        throw error
      }
    },
    []
  )

  return { updateHyperparameters }
}
