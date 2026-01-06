import { useCallback } from 'react'

import {
  approveCompressor,
  createCompressor,
  denyCompressor
} from '@/lib/api/session/compress'
import type {
  CreateCompressorRequest,
  CreateCompressorResponse
} from '@/lib/api/session/compress'
import { addToast } from '@/stores/useToastStore'

export const useCompressorActions = (): {
  approveCompression: (compressorSessionId: string) => Promise<void>
  denyCompression: (compressorSessionId: string) => Promise<void>
  executeCompression: (
    data: CreateCompressorRequest
  ) => Promise<CreateCompressorResponse | void>
} => {
  const executeCompression = useCallback(
    async (data: CreateCompressorRequest): Promise<CreateCompressorResponse | void> => {
      try {
        const response = await createCompressor(data)
        addToast({ status: 'success', title: 'Compression started successfully' })

        return response
      } catch (error: unknown) {
        addToast({
          status: 'failure',
          title: (error as Error).message || 'Failed to start compression'
        })
      }
    },
    []
  )

  const approveCompression = useCallback(
    async (compressorSessionId: string): Promise<void> => {
      try {
        await approveCompressor(compressorSessionId)
        addToast({ status: 'success', title: 'Compression approved successfully' })
      } catch (error: unknown) {
        addToast({
          status: 'failure',
          title: (error as Error).message || 'Failed to approve compression'
        })
      }
    },
    []
  )

  const denyCompression = useCallback(
    async (compressorSessionId: string): Promise<void> => {
      try {
        await denyCompressor(compressorSessionId)
        addToast({ status: 'success', title: 'Compression denied successfully' })
      } catch (error: unknown) {
        addToast({
          status: 'failure',
          title: (error as Error).message || 'Failed to deny compression'
        })
      }
    },
    []
  )

  return {
    executeCompression,
    approveCompression,
    denyCompression
  }
}
