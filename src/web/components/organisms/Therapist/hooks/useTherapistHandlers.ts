import { useCallback, useState } from 'react'

import { applyDoctorModifications } from '@/lib/api/therapist/applyDoctorModifications'
import { useToastStore } from '@/stores/useToastStore'

import type { Diagnosis } from '../types'

type TherapistActions = {
  diagnoseSession: (sessionId: string) => Promise<Diagnosis>
}

type TherapistHandlers = {
  diagnosis: Diagnosis | null
  error: string | null
  isSubmitting: boolean
  selectedDeletions: number[]
  selectedEdits: { turn: number; suggestion: string }[]
  selectedCompressions: { start: number; end: number; reason: string }[]
  handleDiagnose: () => Promise<void>
  handleNewDiagnosis: () => void
  handleApplyModifications: (modifications: {
    deletions?: number[]
    edits?: { turn: number; suggestion: string }[]
    compressions?: { start: number; end: number; reason: string }[]
  }) => Promise<void>
  handleDeletionChange: (
    turn: number
  ) => (event: React.ChangeEvent<HTMLInputElement>) => void
  handleEditChange: (edit: {
    turn: number
    suggestion: string
  }) => (event: React.ChangeEvent<HTMLInputElement>) => void
  handleApply: () => void
}

export const useTherapistHandlers = (
  actions: TherapistActions,
  sessionId: string,
  onRefresh: () => Promise<void>
): TherapistHandlers => {
  const [diagnosis, setDiagnosis] = useState<Diagnosis | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [selectedDeletions, setSelectedDeletions] = useState<number[]>([])
  const [selectedEdits, setSelectedEdits] = useState<
    { turn: number; suggestion: string }[]
  >([])
  const [selectedCompressions, setSelectedCompressions] = useState<
    { start: number; end: number; reason: string }[]
  >([])

  const { addToast } = useToastStore()

  const handleDiagnose = useCallback(async (): Promise<void> => {
    setIsSubmitting(true)
    setError(null)
    try {
      const result = await actions.diagnoseSession(sessionId)
      setDiagnosis(result)
    } catch (error_) {
      setError((error_ as Error).message)
    } finally {
      setIsSubmitting(false)
    }
  }, [actions, sessionId])

  const handleNewDiagnosis = useCallback(() => {
    setDiagnosis(null)
    setSelectedDeletions([])
    setSelectedEdits([])
    setSelectedCompressions([])
  }, [])

  const handleApplyModifications = useCallback(
    async (modifications: {
      deletions?: number[]
      edits?: { turn: number; suggestion: string }[]
      compressions?: { start: number; end: number; reason: string }[]
    }): Promise<void> => {
      setIsSubmitting(true)
      setError(null)
      try {
        const result = await applyDoctorModifications({
          session_id: sessionId,
          modifications
        })
        console.log(result.result)
        if (result.result.status === 'Succeeded') {
          addToast({
            status: 'success',
            title: 'Modifications applied successfully'
          })

          setDiagnosis(null)

          // Refresh the session after modifications
          onRefresh()
        } else if (result.result.status === 'Failed') {
          addToast({
            status: 'failure',
            title: 'Failed to apply modifications',
            description: result.result.reason || 'Unknown error'
          })
        }
      } catch (error_) {
        setError((error_ as Error).message)
        addToast({
          status: 'failure',
          title: 'Failed to apply modifications'
        })
      } finally {
        setIsSubmitting(false)
      }
    },
    [sessionId, addToast, onRefresh]
  )

  const handleDeletionChange = useCallback<
    (turn: number) => (event: React.ChangeEvent<HTMLInputElement>) => void
  >(
    (turn: number) =>
      (event: React.ChangeEvent<HTMLInputElement>): void => {
        const checked = event.target.checked
        if (checked) {
          setSelectedDeletions((previous) => [...previous, turn])
        } else {
          setSelectedDeletions((previous) => previous.filter((t) => t !== turn))
        }
      },
    []
  )

  const handleEditChange = useCallback<
    (edit: {
      turn: number
      suggestion: string
    }) => (event: React.ChangeEvent<HTMLInputElement>) => void
  >(
    (edit: { turn: number; suggestion: string }) =>
      (event: React.ChangeEvent<HTMLInputElement>): void => {
        const checked = event.target.checked
        if (checked) {
          setSelectedEdits((previous) => [...previous, edit])
        } else {
          setSelectedEdits((previous) =>
            previous.filter((element) => element.turn !== edit.turn)
          )
        }
      },
    []
  )

  const handleApply = useCallback((): void => {
    handleApplyModifications({
      deletions: selectedDeletions,
      edits: selectedEdits,
      compressions: selectedCompressions
    })
  }, [handleApplyModifications, selectedDeletions, selectedEdits, selectedCompressions])

  return {
    diagnosis,
    error,
    isSubmitting,
    selectedDeletions,
    selectedEdits,
    selectedCompressions,
    handleDiagnose,
    handleNewDiagnosis,
    handleApplyModifications,
    handleDeletionChange,
    handleEditChange,
    handleApply
  }
}
