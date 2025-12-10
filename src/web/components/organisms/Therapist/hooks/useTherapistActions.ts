import { useCallback } from 'react'

import { createTherapistSession } from '@/lib/api/therapist/createTherapistSession'
import { addToast } from '@/stores/useToastStore'

import type { Diagnosis } from '../types'

type TherapistActions = {
  diagnoseSession: (sessionId: string) => Promise<Diagnosis>
}

export const useTherapistActions = (): TherapistActions => {
  const diagnoseSession = useCallback(async (sessionId: string): Promise<Diagnosis> => {
    try {
      const result = await createTherapistSession({ sessionId: sessionId })
      addToast({ status: 'success', title: 'Diagnosis completed successfully' })

      return result.diagnosis
    } catch (error) {
      addToast({
        status: 'failure',
        title: 'Diagnosis failed',
        description: (error as Error).message
      })
      throw error
    }
  }, [])

  return {
    diagnoseSession
  }
}
