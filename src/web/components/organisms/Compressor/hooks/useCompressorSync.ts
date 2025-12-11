import { useEffect } from 'react'

import type { FormMethods } from '@/components/organisms/Form'

import type { CompressorFormInputs } from '../schema'

type UseCompressorSyncProperties = {
  formContext: FormMethods<CompressorFormInputs> | undefined
  startLocal: number
  endLocal: number
}

export const useCompressorSync = ({
  formContext,
  startLocal,
  endLocal
}: UseCompressorSyncProperties): void => {
  useEffect(() => {
    if (formContext) {
      // Synchronize local state to React Hook Form values
      formContext.setValue('startTurn', startLocal)
      formContext.setValue('endTurn', endLocal)
    }
  }, [formContext, startLocal, endLocal])
}
