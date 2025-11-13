import { useMemo } from 'react'

import type { ProcedureOption } from '@/lib/api/procedures/getProcedures'

export const useProceduresHandlers = (
  procedureOptions: ProcedureOption[]
): {
  filteredProcedureOptions: ProcedureOption[]
} => {
  const filteredProcedureOptions = useMemo(() => procedureOptions, [procedureOptions])

  return {
    filteredProcedureOptions
  }
}
