import { useCallback } from 'react'

import { useToast } from '@/components/organisms/Toast/hooks/useToast'
import { editHyperparameters } from '@/lib/api/session/editHyperparameters'
import type { EditHyperparametersRequest } from '@/lib/api/session/editHyperparameters'
import type { SessionDetail } from '@/lib/api/session/getSession'

export const useHyperParametersActions = (): {
  updateHyperparameters: (
    sessionId: string,
    payload: EditHyperparametersRequest,
  ) => Promise<{ message: string; session: SessionDetail }>
} => {
  const toast = useToast()

  const updateHyperparameters = useCallback(
    async (sessionId: string, payload: EditHyperparametersRequest) => {
      try {
        const result = await editHyperparameters(sessionId, payload)
        toast.success(result?.message || 'Hyperparameters updated')

        return result
      } catch (error: unknown) {
        toast.failure((error as Error).message || 'Failed to update hyperparameters')
        throw error
      }
    },
    [toast],
  )

  return { updateHyperparameters }
}
