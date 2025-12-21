import { useCallback } from 'react'

import { useToast } from '@/components/organisms/Toast/hooks/useToast'
import { editArtifacts } from '@/lib/api/session/editArtifacts'

type UseArtifactListActionsReturn = {
  updateArtifacts: (sessionId: string, artifactPaths: string[]) => Promise<void>
}

export const useArtifactListActions = (): UseArtifactListActionsReturn => {
  const toast = useToast()

  const updateArtifacts = useCallback(
    async (sessionId: string, artifactPaths: string[]): Promise<void> => {
      try {
        await editArtifacts(sessionId, artifactPaths)
        toast.success('Artifacts updated successfully')
      } catch (error) {
        toast.failure(
          `Failed to update artifacts: ${error instanceof Error ? error.message : 'Unknown error'}`
        )
      }
    },
    [toast]
  )

  return {
    updateArtifacts
  }
}
