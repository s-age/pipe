import { useCallback } from 'react'

import { editReferencePersist } from '@/lib/api/meta/editReferencePersist'
import { editReferenceTtl } from '@/lib/api/meta/editReferenceTtl'
import { toggleReferenceDisabled } from '@/lib/api/meta/toggleReferenceDisabled'
import { addToast } from '@/stores/useToastStore'

export const useReferenceActions = (): {
  handleToggleReferenceDisabled: (sessionId: string, index: number) => Promise<void>
  handleUpdateReferencePersist: (
    sessionId: string,
    index: number,
    persist: boolean
  ) => Promise<void>
  handleUpdateReferenceTtl: (
    sessionId: string,
    index: number,
    ttl: number
  ) => Promise<void>
} => {
  const handleUpdateReferencePersist = useCallback(
    async (sessionId: string, index: number, persist: boolean): Promise<void> => {
      try {
        await editReferencePersist(sessionId, index, persist)
        addToast({
          status: 'success',
          title: 'Reference persist state updated successfully'
        })
      } catch (error: unknown) {
        addToast({
          status: 'failure',
          title: (error as Error).message || 'Failed to update reference persist state.'
        })
      }
    },
    []
  )

  const handleUpdateReferenceTtl = useCallback(
    async (sessionId: string, index: number, ttl: number): Promise<void> => {
      try {
        await editReferenceTtl(sessionId, index, ttl)
        addToast({ status: 'success', title: 'Reference TTL updated successfully' })
      } catch (error: unknown) {
        addToast({
          status: 'failure',
          title: (error as Error).message || 'Failed to update reference TTL.'
        })
      }
    },
    []
  )

  const handleToggleReferenceDisabled = useCallback(
    async (sessionId: string, index: number): Promise<void> => {
      try {
        await toggleReferenceDisabled(sessionId, index)
        addToast({
          status: 'success',
          title: 'Reference disabled state updated successfully'
        })
      } catch (error: unknown) {
        addToast({
          status: 'failure',
          title:
            (error as Error).message || 'Failed to update reference disabled state.'
        })
      }
    },
    []
  )

  return {
    handleUpdateReferencePersist,
    handleUpdateReferenceTtl,
    handleToggleReferenceDisabled
  }
}
