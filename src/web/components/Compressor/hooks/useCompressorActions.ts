import { useCallback } from 'react'

import { client } from '@/lib/api/client'

import type { CompressorFormInputs } from '../schema'

type UseCompressorActionsProperties = {
  sessionId: string
}

type UseCompressorActionsReturn = {
  submitCompression: (data: CompressorFormInputs) => Promise<unknown>
}

export const useCompressorActions = ({
  sessionId
}: UseCompressorActionsProperties): UseCompressorActionsReturn => {
  const submitCompression = useCallback(
    async (data: CompressorFormInputs): Promise<unknown> => {
      const payload = {
        session: sessionId || undefined,
        instruction: `Compress to approximately ${data.targetLength || '[unspecified]'} characters. Policy: ${data.policy}`,
        target_length: data.targetLength || undefined,
        start_turn: data.startTurn || undefined,
        end_turn: data.endTurn || undefined
      }

      return client.post('/compress', { body: payload })
    },
    [sessionId]
  )

  return {
    submitCompression
  }
}
