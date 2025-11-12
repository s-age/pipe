import { useCallback } from 'react'

import { useFileSearchExplorerActions } from '@/components/organisms/FileSearchExplorer/hooks/useFileSearchExplorerActions'
import type { SessionDetail } from '@/lib/api/session/getSession'

import { useReferenceActions } from './useReferenceActions'

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
  const referenceActions = useReferenceActions(sessionDetail, refreshSessions)
  const fileActions = useFileSearchExplorerActions()

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
        await referenceActions.handleAddReference(currentSessionId, path)
      }
    },
    [referenceActions, currentSessionId]
  )

  return {
    loadRootSuggestions,
    loadSubDirectorySuggestions,
    addReference
  }
}
