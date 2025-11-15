import { useCallback, useMemo } from 'react'

import type { ProcedureOption } from '@/lib/api/procedures/getProcedures'
import { emitToast } from '@/lib/toastEvents'

import type { UseProceduresActionsReturn } from './useProceduresActions'

export const useProceduresHandlers = (
  procedureOptions: ProcedureOption[],
  actions: UseProceduresActionsReturn,
  setProcedureOptions: React.Dispatch<React.SetStateAction<ProcedureOption[]>>
): {
  filteredProcedureOptions: ProcedureOption[]
  handleFetchProcedures: () => Promise<void>
} => {
  const filteredProcedureOptions = useMemo(() => procedureOptions, [procedureOptions])

  const handleFetchProcedures = useCallback(async (): Promise<void> => {
    try {
      const procedures = await actions.fetchProcedures()
      setProcedureOptions(procedures)
    } catch (error: unknown) {
      emitToast.failure((error as Error).message || 'Failed to fetch procedures.')
    }
  }, [actions, setProcedureOptions])

  return {
    filteredProcedureOptions,
    handleFetchProcedures
  }
}
