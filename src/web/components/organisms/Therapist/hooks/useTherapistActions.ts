import { useCallback } from 'react'

import { applyDoctorModifications as applyDoctorModificationsApi } from '@/lib/api/therapist/applyDoctorModifications'
import { createTherapistSession } from '@/lib/api/therapist/createTherapistSession'
import { addToast } from '@/stores/useToastStore'

import type { Diagnosis } from '../types'

type TherapistActions = {
  diagnoseSession: (sessionId: string) => Promise<Diagnosis | void>
  applyModifications: (
    sessionId: string,
    modifications: {
      deletions?: number[]
      edits?: { turn: number; newContent: string }[]
      compressions?: { start: number; end: number; reason: string }[]
    }
  ) => Promise<void>
}

export const useTherapistActions = (): TherapistActions => {
  const diagnoseSession = useCallback(
    async (sessionId: string): Promise<Diagnosis | void> => {
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
      }
    },
    []
  )

  const applyModifications = useCallback(
    async (
      sessionId: string,
      modifications: {
        deletions?: number[]
        edits?: { turn: number; newContent: string }[]
        compressions?: { start: number; end: number; reason: string }[]
      }
    ): Promise<void> => {
      try {
        const result = await applyDoctorModificationsApi({
          sessionId,
          modifications
        })

        if (result.result.status === 'Succeeded') {
          addToast({
            status: 'success',
            title: 'Modifications applied successfully'
          })
        } else if (result.result.status === 'Failed') {
          addToast({
            status: 'failure',
            title: 'Failed to apply modifications',
            description: result.result.reason || 'Unknown error'
          })
        }
      } catch (error) {
        addToast({
          status: 'failure',
          title: 'Failed to apply modifications',
          description: (error as Error).message
        })
      }
    },
    []
  )

  return {
    diagnoseSession,
    applyModifications
  }
}
