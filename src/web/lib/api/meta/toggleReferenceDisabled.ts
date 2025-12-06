import { client } from '../client'

export type ToggleReferenceDisabledResponse = {
  message: string
  disabled: boolean
}

export const toggleReferenceDisabled = async (
  sessionId: string,
  referenceIndex: number
): Promise<ToggleReferenceDisabledResponse> =>
  client.patch<ToggleReferenceDisabledResponse>(
    `/session/${sessionId}/references/${referenceIndex}/toggle`
  )
