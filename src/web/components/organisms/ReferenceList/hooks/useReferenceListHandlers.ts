import { useCallback, useMemo } from 'react'
import type { UseFormReturn } from 'react-hook-form'

import { useFileSearchExplorerActions } from '@/components/organisms/FileSearchExplorer/hooks/useFileSearchExplorerActions'
import type { Reference } from '@/types/reference'

export const useReferenceListHandlers = (
  formContext: UseFormReturn | undefined,
  references: Reference[]
): {
  actions: {
    loadRootSuggestions: () => Promise<{ name: string; isDirectory: boolean }[]>
    loadSubDirectorySuggestions: (
      pathParts: string[]
    ) => Promise<{ name: string; isDirectory: boolean }[]>
    addReference: (path: string) => Promise<void>
  }
} => {
  const addReference = useCallback(
    async (path: string): Promise<void> => {
      const newReference: Reference = {
        path,
        ttl: 3,
        persist: false,
        disabled: false
      }
      formContext?.setValue?.('references', [...references, newReference])
    },
    [formContext, references]
  )

  const fileActions = useFileSearchExplorerActions()
  const actions = useMemo(
    () => ({
      loadRootSuggestions: async (): Promise<
        { name: string; isDirectory: boolean }[]
      > => {
        const lsResult = await fileActions.getLsData({ final_path_list: [] })
        if (lsResult) {
          return lsResult.entries.map((entry) => ({
            name: entry.name,
            isDirectory: entry.is_dir
          }))
        }

        return []
      },
      loadSubDirectorySuggestions: async (
        pathParts: string[]
      ): Promise<{ name: string; isDirectory: boolean }[]> => {
        const lsResult = await fileActions.getLsData({ final_path_list: pathParts })
        if (lsResult) {
          return lsResult.entries.map((entry) => ({
            name: entry.name,
            isDirectory: entry.is_dir
          }))
        }

        return []
      },
      addReference
    }),
    [addReference, fileActions]
  )

  return {
    actions
  }
}
