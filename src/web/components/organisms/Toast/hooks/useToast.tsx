import { useCallback } from 'react'

import { useAppStore } from '@/stores/useAppStore'

type ToastParameters = {
  status: 'success' | 'failure' | 'warning'
  title?: string
  description?: string
  position?:
    | 'top-left'
    | 'top-center'
    | 'top-right'
    | 'bottom-left'
    | 'bottom-center'
    | 'bottom-right'
  duration?: number | null
}

type UseToast = {
  show: (parameters: ToastParameters) => string
  success: (titleOrParameters: string | Partial<ToastParameters>) => string
  failure: (titleOrParameters: string | Partial<ToastParameters>) => string
  warning: (titleOrParameters: string | Partial<ToastParameters>) => string
}

const useToast = (): UseToast => {
  const { pushToast } = useAppStore()

  const show = useCallback(
    (parameters: ToastParameters): string => pushToast(parameters),
    [pushToast],
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
    },
  }
}

export default useToast
