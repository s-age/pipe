import { useMemo } from 'react'

import type { SessionDetail } from '@/lib/api/session/getSession'
import type { Settings } from '@/types/settings'

import type { StartSessionFormInputs } from '../schema'

type UseStartSessionFormLifecycleProperties = {
  settings: Settings
  defaultValuesFromParent?: Partial<StartSessionFormInputs> | null
}

export const useStartSessionFormLifecycle = ({
  settings,
  defaultValuesFromParent
}: UseStartSessionFormLifecycleProperties): {
  computedDefaultValues: StartSessionFormInputs
  sessionDetail: SessionDetail
} => {
  const computedDefaultValues = useMemo((): StartSessionFormInputs => {
    if (defaultValuesFromParent)
      return defaultValuesFromParent as StartSessionFormInputs

    return {
      session_id: '',
      purpose: '',
      background: '',
      roles: [],
      parent: null,
      references: [],
      artifacts: [],
      procedure: null,
      instruction: '',
      turns: [],
      multi_step_reasoning_enabled: false,
      hyperparameters: settings.hyperparameters,
      todos: []
    }
    // only re-create when settings.hyperparameters changes
  }, [defaultValuesFromParent, settings.hyperparameters])

  const sessionDetail = useMemo(
    () => ({ ...computedDefaultValues, turns: [] }) as SessionDetail,
    [computedDefaultValues]
  )

  return {
    computedDefaultValues,
    sessionDetail
  }
}
