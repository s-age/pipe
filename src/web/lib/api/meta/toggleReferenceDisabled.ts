import { client } from '../client'

export type ToggleReferenceDisabledResponse = {
  disabled: boolean
  message: string
}

export const toggleReferenceDisabled = async (
  sessionId: string,
  referenceIndex: number
): Promise<ToggleReferenceDisabledResponse> =>
  client.patch<ToggleReferenceDisabledResponse>(
    `/session/${sessionId}/references/${referenceIndex}/toggle`
  )
