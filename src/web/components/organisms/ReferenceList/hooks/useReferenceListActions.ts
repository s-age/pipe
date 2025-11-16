import { useCallback } from 'react'

import { useFileSearchExplorerActions } from '@/components/organisms/FileSearchExplorer/hooks/useFileSearchExplorerActions'
import { editReferences } from '@/lib/api/session/editReferences'
import { getSession } from '@/lib/api/session/getSession'
import { emitToast } from '@/lib/toastEvents'
import type { Reference } from '@/types/reference'

export const useReferenceListActions = (
  currentSessionId: string | null
): {
  loadRootSuggestions: () => Promise<{ name: string; isDirectory: boolean }[]>
  loadSubDirectorySuggestions: (
    pathParts: string[]
  ) => Promise<{ name: string; isDirectory: boolean }[]>
  handleUpdateReference: (newReferences: Reference[]) => Promise<Reference[] | void>
} => {
  const fileActions = useFileSearchExplorerActions()

  const handleUpdateReference = useCallback(
    async (newReferences: Reference[]): Promise<Reference[] | void> => {
      console.log(currentSessionId, newReferences)
      if (!currentSessionId) return

      try {
        await editReferences(currentSessionId, newReferences)
        const { session } = await getSession(currentSessionId)
        console.log(session.references)
        emitToast.success('Reference added successfully')

        return session.references
      } catch (error: unknown) {
        emitToast.failure((error as Error).message || 'Failed to add reference.')
        throw error
      }
    },
    [currentSessionId]
  )

  const loadRootSuggestions = useCallback(async () => {
    if (currentSessionId) {
      try {
        const lsResult = await fileActions.getLsData({ final_path_list: [] })
        if (lsResult) {
          const rootEntries = lsResult.entries.map((entry) => ({
            name: entry.name,
            isDirectory: entry.is_dir
          }))
          emitToast.success('Root suggestions loaded successfully')

          return rootEntries
        }
      } catch (error: unknown) {
        emitToast.failure(
          (error as Error).message || 'Failed to load root suggestions.'
        )
      }
    }

    return []
  }, [fileActions, currentSessionId])

  const loadSubDirectorySuggestions = useCallback(
    async (pathParts: string[]) => {
      try {
        const lsResult = await fileActions.getLsData({ final_path_list: pathParts })
        if (lsResult) {
          const entries = lsResult.entries.map((entry) => ({
            name: entry.name,
            isDirectory: entry.is_dir
          }))
          emitToast.success('Sub-directory suggestions loaded successfully')

          return entries
        }
      } catch (error: unknown) {
        emitToast.failure(
          (error as Error).message || 'Failed to load sub-directory suggestions.'
        )
      }

      return []
    },
    [fileActions]
  )

  return {
    loadRootSuggestions,
    loadSubDirectorySuggestions,
    handleUpdateReference
  }
}
