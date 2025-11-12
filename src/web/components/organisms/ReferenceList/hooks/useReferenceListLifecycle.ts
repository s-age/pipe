import { useEffect } from 'react'

export const useReferenceListLifecycle = (
  actions: {
    loadRootSuggestions: () => Promise<{ name: string; isDirectory: boolean }[]>
  },
  setRootSuggestions: (suggestions: { name: string; isDirectory: boolean }[]) => void
): void => {
  useEffect(() => {
    void actions.loadRootSuggestions().then(setRootSuggestions)
  }, [actions, setRootSuggestions])
}
