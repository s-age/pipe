import { useCallback } from 'react'

import { editHyperparameters } from '@/lib/api/meta/editHyperparameters'
import type { EditHyperparametersRequest } from '@/lib/api/meta/editHyperparameters'
import type { SessionDetail } from '@/lib/api/session/getSession'
import { addToast } from '@/stores/useToastStore'

export const useHyperParametersActions = (): {
  updateHyperparameters: (
    sessionId: string,
    payload: EditHyperparametersRequest
  ) => Promise<{ message: string; session: SessionDetail } | void>
} => {
  const updateHyperparameters = useCallback(
    async (
      sessionId: string,
      payload: EditHyperparametersRequest
    ): Promise<{ message: string; session: SessionDetail } | void> => {
      try {
        const result = await editHyperparameters(sessionId, payload)
        addToast({
          status: 'success',
          title: result?.message || 'Hyperparameters updated'
        })

        return result
      } catch (error: unknown) {
        addToast({
          status: 'failure',
          title: (error as Error).message || 'Failed to update hyperparameters'
        })
      }
    },
    []
  )

  return { updateHyperparameters }
}
