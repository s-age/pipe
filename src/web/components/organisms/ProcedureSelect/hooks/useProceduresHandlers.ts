import { useCallback, useMemo } from 'react'

import type { ProcedureOption } from '@/lib/api/procedures/getProcedures'

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
    const procedures = await actions.fetchProcedures()
    if (procedures) {
      setProcedureOptions(procedures)
    }
  }, [actions, setProcedureOptions])

  return {
    filteredProcedureOptions,
    handleFetchProcedures
  }
}
