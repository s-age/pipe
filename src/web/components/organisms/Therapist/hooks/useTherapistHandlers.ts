import { useCallback, useState } from 'react'

import type { Diagnosis } from '../types'
import { useTherapistActions } from './useTherapistActions'

type TherapistHandlers = {
  diagnosis: Diagnosis | null
  isSubmitting: boolean
  selectedCompressions: { end: number; reason: string; start: number }[]
  selectedDeletions: number[]
  selectedEdits: { newContent: string; turn: number }[]
  handleApply: () => void
  handleApplyModifications: (modifications: {
    compressions?: { end: number; reason: string; start: number }[]
    deletions?: number[]
    edits?: { newContent: string; turn: number }[]
  }) => Promise<void>
  handleDeletionChange: (
    turn: number
  ) => (event: React.ChangeEvent<HTMLInputElement>) => void
  handleDiagnose: () => Promise<void>
  handleEditChange: (edit: {
    newContent: string
    turn: number
  }) => (event: React.ChangeEvent<HTMLInputElement>) => void
}

export const useTherapistHandlers = (
  sessionId: string,
  onRefresh: () => Promise<void>
): TherapistHandlers => {
  const { applyModifications, diagnoseSession } = useTherapistActions()

  const [diagnosis, setDiagnosis] = useState<Diagnosis | null>(null)
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [selectedDeletions, setSelectedDeletions] = useState<number[]>([])
  const [selectedEdits, setSelectedEdits] = useState<
    { newContent: string; turn: number }[]
  >([])
  const [selectedCompressions, setSelectedCompressions] = useState<
    { end: number; reason: string; start: number }[]
  >([])

  const handleDiagnose = useCallback(async (): Promise<void> => {
    setDiagnosis(null)
    setIsSubmitting(true)

    const result = await diagnoseSession(sessionId)
    if (result) {
      setDiagnosis(result)
      setSelectedDeletions([])
      setSelectedEdits([])
      setSelectedCompressions([])
    }

    setIsSubmitting(false)
  }, [diagnoseSession, sessionId])

  const handleApplyModifications = useCallback(
    async (modifications: {
      compressions?: { end: number; reason: string; start: number }[]
      deletions?: number[]
      edits?: { newContent: string; turn: number }[]
    }): Promise<void> => {
      setIsSubmitting(true)

      await applyModifications(sessionId, modifications)

      setDiagnosis(null)
      await onRefresh()

      setIsSubmitting(false)
    },
    [sessionId, applyModifications, onRefresh]
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
      newContent: string
      turn: number
    }) => (event: React.ChangeEvent<HTMLInputElement>) => void
  >(
    (edit: { newContent: string; turn: number }) =>
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
    isSubmitting,
    selectedDeletions,
    selectedEdits,
    selectedCompressions,
    handleDiagnose,
    handleApplyModifications,
    handleDeletionChange,
    handleEditChange,
    handleApply
  }
}
