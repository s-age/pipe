import { useCallback } from 'react'

import { useInitialLoading } from '@/hooks/useInitialLoading'
import { getSessionTree } from '@/lib/api/sessionTree/getSessionTree'
import type { useSessionStore } from '@/stores/useChatHistoryStore'
import { useToastStore } from '@/stores/useToastStore'

type Properties = {
  storeActions: ReturnType<typeof useSessionStore>['actions']
}

export const useSessionManagementLifecycle = ({ storeActions }: Properties): void => {
  const { addToast } = useToastStore()

  const loadSessions = useCallback<() => Promise<void>>(async (): Promise<void> => {
    try {
      const sessionTree = await getSessionTree()
      const sessions =
        sessionTree.session_tree ||
        sessionTree.sessions.map(([_, overview]) => overview)
      storeActions.setSessions(sessions)
    } catch {
      addToast({
        status: 'failure',
        title: 'Failed to load sessions.'
      })
    }
  }, [storeActions, addToast])

  useInitialLoading(loadSessions)
}
