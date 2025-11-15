import { useCallback } from 'react'

import { editHyperparameters } from '@/lib/api/session/editHyperparameters'
import type { EditHyperparametersRequest } from '@/lib/api/session/editHyperparameters'
import type { SessionDetail } from '@/lib/api/session/getSession'

export const useHyperParametersActions = (): {
  updateHyperparameters: (
    sessionId: string,
    payload: EditHyperparametersRequest
  ) => Promise<{ message: string; session: SessionDetail }>
} => {
  const updateHyperparameters = useCallback(
    async (sessionId: string, payload: EditHyperparametersRequest) => {
      const result = await editHyperparameters(sessionId, payload)

      return result
    },
    []
  )

  return { updateHyperparameters }
}
