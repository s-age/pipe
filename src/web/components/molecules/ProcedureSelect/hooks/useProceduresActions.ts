import { useCallback } from 'react'

import { getProcedures, type ProcedureOption } from '@/lib/api/procedures/getProcedures'

export const useProceduresActions = (): {
  fetchProcedures: () => Promise<ProcedureOption[]>
} => {
  const fetchProcedures = useCallback(
    async (): Promise<ProcedureOption[]> => getProcedures(),
    []
  )

  return {
    fetchProcedures
  }
}
