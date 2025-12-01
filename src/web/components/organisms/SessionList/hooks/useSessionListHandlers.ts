import type {
  SessionOverview,
  SessionTreeNode
} from '@/lib/api/sessionTree/getSessionTree'

export const useSessionListHandlers = (
  sessions: SessionOverview[] | SessionTreeNode[],
  allSelected: boolean,
  onSelectAll: (
    sessions: SessionOverview[] | SessionTreeNode[],
    isSelected: boolean
  ) => void
): { handleSelectAll: () => void } => {
  const handleSelectAll = (): void => {
    onSelectAll(sessions, !allSelected)
  }

  return {
    handleSelectAll
  }
}
