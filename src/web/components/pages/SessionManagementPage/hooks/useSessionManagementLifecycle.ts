import { useCallback } from 'react'

import { useInitialLoading } from '@/hooks/useInitialLoading'
import { getSessionManagement } from '@/lib/api/bff/getSessionManagement'
import type { useSessionStore } from '@/stores/useChatHistoryStore'
import { useToastStore } from '@/stores/useToastStore'

type Properties = {
  storeActions: ReturnType<typeof useSessionStore>['actions']
}

export const useSessionManagementLifecycle = ({ storeActions }: Properties): void => {
  const { addToast } = useToastStore()

  const loadData = useCallback<() => Promise<void>>(async (): Promise<void> => {
    try {
      const { sessionTree, archives } = await getSessionManagement()
      const sessions = sessionTree.map((node) => node.overview)
      storeActions.setSessions(sessions)
      storeActions.setArchivedSessions(archives)
    } catch {
      addToast({
        status: 'failure',
        title: 'Failed to load session management data.'
      })
    }
  }, [storeActions, addToast])

  useInitialLoading(loadData)
}
