import { useCallback } from 'react'

import { useOptionalFormContext } from '@/components/organisms/Form'

import { useCompressorActions } from './useCompressorActions'
import type { UseCompressorActionsProperties } from './useCompressorActions'

export const useCompressorFormLogic = (
  properties: UseCompressorActionsProperties
): { onExecuteClick: () => void } => {
  const formContext = useOptionalFormContext()
  const { handleExecute } = useCompressorActions(properties)

  const onExecuteClick = useCallback((): void => {
    const values = formContext?.getValues()
    if (values) {
      void handleExecute(values as never)
    }
  }, [formContext, handleExecute])

  return { onExecuteClick }
}
