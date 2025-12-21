import { client } from '../client'

export type EditArtifactsRequest = {
  artifacts: Array<{ path: string; contents: null }>
}

export type EditArtifactsResponse = {
  message: string
}

export const editArtifacts = async (
  sessionId: string,
  artifactPaths: string[]
): Promise<EditArtifactsResponse> => {
  const payload: EditArtifactsRequest = {
    artifacts: artifactPaths.map((path) => ({
      path,
      contents: null
    }))
  }

  return client.patch<EditArtifactsResponse>(`/session/${sessionId}/artifacts`, {
    body: payload
  })
}
