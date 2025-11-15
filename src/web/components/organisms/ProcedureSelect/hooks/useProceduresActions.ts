import { useCallback } from 'react'

import { getProcedures, type ProcedureOption } from '@/lib/api/procedures/getProcedures'

export type UseProceduresActionsReturn = {
  fetchProcedures: () => Promise<ProcedureOption[]>
}

export const useProceduresActions = (): UseProceduresActionsReturn => {
  const fetchProcedures = useCallback(
    async (): Promise<ProcedureOption[]> => getProcedures(),
    []
  )

  return {
    fetchProcedures
  }
}
