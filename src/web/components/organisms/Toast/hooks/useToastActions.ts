import { useCallback } from 'react'

import { useAppStore } from '@/stores/useAppStore'

type ToastParameters = {
  status: 'success' | 'failure' | 'warning'
  description?: string
  duration?: number | null
  position?:
    | 'top-left'
    | 'top-center'
    | 'top-right'
    | 'bottom-left'
    | 'bottom-center'
    | 'bottom-right'
  title?: string
}

export type UseToastActions = {
  failure: (titleOrParameters: string | Partial<ToastParameters>) => string
  show: (parameters: ToastParameters) => string
  success: (titleOrParameters: string | Partial<ToastParameters>) => string
  warning: (titleOrParameters: string | Partial<ToastParameters>) => string
}

export const useToastActions = (): UseToastActions => {
  const { pushToast } = useAppStore()

  const show = useCallback(
    (parameters: ToastParameters): string => pushToast(parameters),
    [pushToast]
  )

  return {
    show,
    success: (titleOrParameters: string | Partial<ToastParameters>): string => {
      if (typeof titleOrParameters === 'string')
        return pushToast({ status: 'success', title: titleOrParameters })

      return pushToast({ ...(titleOrParameters as ToastParameters), status: 'success' })
    },
    failure: (titleOrParameters: string | Partial<ToastParameters>): string => {
      if (typeof titleOrParameters === 'string')
        return pushToast({ status: 'failure', title: titleOrParameters })

      return pushToast({ ...(titleOrParameters as ToastParameters), status: 'failure' })
    },
    warning: (titleOrParameters: string | Partial<ToastParameters>): string => {
      if (typeof titleOrParameters === 'string')
        return pushToast({ status: 'warning', title: titleOrParameters })

      return pushToast({ ...(titleOrParameters as ToastParameters), status: 'warning' })
    }
  }
}
