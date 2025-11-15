import { useCallback } from 'react'

import { useFileSearchExplorerActions } from '@/components/organisms/FileSearchExplorer/hooks/useFileSearchExplorerActions'
import { editReferences } from '@/lib/api/session/editReferences'
import type { SessionDetail } from '@/lib/api/session/getSession'
import type { Reference } from '@/types/reference'

export const useReferenceListActions = (
  sessionDetail: SessionDetail | null,
  currentSessionId: string | null,
  refreshSessions?: () => Promise<void>
): {
  loadRootSuggestions: () => Promise<{ name: string; isDirectory: boolean }[]>
  loadSubDirectorySuggestions: (
    pathParts: string[]
  ) => Promise<{ name: string; isDirectory: boolean }[]>
  addReference: (path: string) => Promise<void>
} => {
  const fileActions = useFileSearchExplorerActions()

  const handleAddReference = useCallback(
    async (sessionId: string, path: string): Promise<void> => {
      if (!sessionId) return
      const newReference: Reference = {
        path,
        disabled: false,
        persist: false,
        ttl: 3
      }
      // const newReferences = [...sessionDetail.references, newReference]
      const newReferences = [newReference] // --- IGNORE ---
      await editReferences(sessionId, newReferences)
      if (refreshSessions) await refreshSessions()
    },
    [refreshSessions]
  )

  const loadRootSuggestions = useCallback(async () => {
    if (sessionDetail?.references) {
      const lsResult = await fileActions.getLsData({ final_path_list: [] })
      if (lsResult) {
        const rootEntries = lsResult.entries.map((entry) => ({
          name: entry.name,
          isDirectory: entry.is_dir
        }))

        return rootEntries
      }
    }

    return []
  }, [fileActions, sessionDetail?.references])

  const loadSubDirectorySuggestions = useCallback(
    async (pathParts: string[]) => {
      const lsResult = await fileActions.getLsData({ final_path_list: pathParts })
      if (lsResult) {
        const entries = lsResult.entries.map((entry) => ({
          name: entry.name,
          isDirectory: entry.is_dir
        }))

        return entries
      }

      return []
    },
    [fileActions]
  )

  const addReference = useCallback(
    async (path: string) => {
      if (currentSessionId) {
        await handleAddReference(currentSessionId, path)
      }
    },
    [handleAddReference, currentSessionId]
  )

  return {
    loadRootSuggestions,
    loadSubDirectorySuggestions,
    addReference
  }
}
