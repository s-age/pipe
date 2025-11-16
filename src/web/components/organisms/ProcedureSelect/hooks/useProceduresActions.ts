import { useCallback } from 'react'

import { getProcedures, type ProcedureOption } from '@/lib/api/procedures/getProcedures'
import { emitToast } from '@/lib/toastEvents'

export type UseProceduresActionsReturn = {
  fetchProcedures: () => Promise<ProcedureOption[] | void>
}

export const useProceduresActions = (): UseProceduresActionsReturn => {
  const fetchProcedures = useCallback(async (): Promise<ProcedureOption[] | void> => {
    try {
      const procedures = await getProcedures()

      return procedures
    } catch (error: unknown) {
      emitToast.failure((error as Error).message || 'Failed to fetch procedures.')
    }
  }, [])

  return {
    fetchProcedures
  }
}
