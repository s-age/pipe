import { useCallback } from 'react'

import { useFileSearchExplorerActions } from '@/components/organisms/FileSearchExplorer/hooks/useFileSearchExplorerActions'
import type { BrowseResponse } from '@/lib/api/fs/browse'
import { editReferences } from '@/lib/api/meta/editReferences'
import { getSession } from '@/lib/api/session/getSession'
import { addToast } from '@/stores/useToastStore'
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
      if (!currentSessionId) return

      try {
        await editReferences(currentSessionId, newReferences)
        const sessionDetail = await getSession(currentSessionId)
        addToast({ status: 'success', title: 'Reference added successfully' })

        return sessionDetail.references
      } catch (error: unknown) {
        addToast({
          status: 'failure',
          title: (error as Error).message || 'Failed to add reference.'
        })
      }
    },
    [currentSessionId]
  )

  const loadRootSuggestions = useCallback(async () => {
    if (currentSessionId) {
      try {
        const lsResult = await fileActions.browseDirectory({ finalPathList: [] })
        if (lsResult) {
          const rootEntries = lsResult.entries.map(
            (entry: BrowseResponse['entries'][number]) => ({
              name: entry.name,
              isDirectory: entry.isDir
            })
          )
          addToast({ status: 'success', title: 'Root suggestions loaded successfully' })

          return rootEntries
        }
      } catch (error: unknown) {
        addToast({
          status: 'failure',
          title: (error as Error).message || 'Failed to load root suggestions.'
        })
      }
    }

    return []
  }, [fileActions, currentSessionId])

  const loadSubDirectorySuggestions = useCallback(
    async (pathParts: string[]) => {
      try {
        const lsResult = await fileActions.browseDirectory({ finalPathList: pathParts })
        if (lsResult) {
          const entries = lsResult.entries.map(
            (entry: BrowseResponse['entries'][number]) => ({
              name: entry.name,
              isDirectory: entry.isDir
            })
          )
          addToast({
            status: 'success',
            title: 'Sub-directory suggestions loaded successfully'
          })

          return entries
        }
      } catch (error: unknown) {
        addToast({
          status: 'failure',
          title: (error as Error).message || 'Failed to load sub-directory suggestions.'
        })
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
