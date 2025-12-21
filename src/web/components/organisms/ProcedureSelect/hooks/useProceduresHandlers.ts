import { useCallback, useState } from 'react'
import type { UseFormReturn } from 'react-hook-form'

import type { ProcedureOption } from '@/lib/api/fs/procedures'

import type { UseProceduresActionsReturn } from './useProceduresActions'

export const useProceduresHandlers = (
  actions: UseProceduresActionsReturn,
  formContext: UseFormReturn | undefined
): {
  procedureOptions: ProcedureOption[]
  handleFetchProcedures: () => Promise<void>
  handleFocus: () => Promise<void>
  handleProcedureChange: (values: string[]) => void
} => {
  const [procedureOptions, setProcedureOptions] = useState<ProcedureOption[]>([])

  const handleFetchProcedures = useCallback(async (): Promise<void> => {
    const procedures = await actions.fetchProcedures()
    if (procedures) {
      setProcedureOptions(procedures)
    }
  }, [actions])

  const handleFocus = useCallback(async () => {
    if (procedureOptions.length === 0) {
      void handleFetchProcedures()
    }
  }, [procedureOptions.length, handleFetchProcedures])

  const handleProcedureChange = useCallback(
    (values: string[]): void => {
      if (formContext?.setValue) {
        formContext.setValue('procedure', values[0] || '')
      }
    },
    [formContext]
  )

  return {
    procedureOptions,
    handleFetchProcedures,
    handleFocus,
    handleProcedureChange
  }
}
