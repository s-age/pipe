import { useCallback, useState } from 'react'

import type { Diagnosis } from '../types'
import { useTherapistActions } from './useTherapistActions'

type TherapistHandlers = {
  diagnosis: Diagnosis | null
  isSubmitting: boolean
  selectedDeletions: number[]
  selectedEdits: { turn: number; newContent: string }[]
  selectedCompressions: { start: number; end: number; reason: string }[]
  handleDiagnose: () => Promise<void>
  handleApplyModifications: (modifications: {
    deletions?: number[]
    edits?: { turn: number; newContent: string }[]
    compressions?: { start: number; end: number; reason: string }[]
  }) => Promise<void>
  handleDeletionChange: (
    turn: number
  ) => (event: React.ChangeEvent<HTMLInputElement>) => void
  handleEditChange: (edit: {
    turn: number
    newContent: string
  }) => (event: React.ChangeEvent<HTMLInputElement>) => void
  handleApply: () => void
}

export const useTherapistHandlers = (
  sessionId: string,
  onRefresh: () => Promise<void>
): TherapistHandlers => {
  const { diagnoseSession, applyModifications } = useTherapistActions()

  const [diagnosis, setDiagnosis] = useState<Diagnosis | null>(null)
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [selectedDeletions, setSelectedDeletions] = useState<number[]>([])
  const [selectedEdits, setSelectedEdits] = useState<
    { turn: number; newContent: string }[]
  >([])
  const [selectedCompressions, setSelectedCompressions] = useState<
    { start: number; end: number; reason: string }[]
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
      deletions?: number[]
      edits?: { turn: number; newContent: string }[]
      compressions?: { start: number; end: number; reason: string }[]
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
      turn: number
      newContent: string
    }) => (event: React.ChangeEvent<HTMLInputElement>) => void
  >(
    (edit: { turn: number; newContent: string }) =>
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
