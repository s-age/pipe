import type { Settings } from '@/types/settings'

import { client } from '../client'
import type { SessionOverview } from '../sessionTree/getSessionTree'

export type StartSessionSettingsResponse = {
  settings: Settings
  session_tree: [string, SessionOverview][]
}

export const getStartSessionSettings =
  async (): Promise<StartSessionSettingsResponse> =>
    client.get<StartSessionSettingsResponse>(`/bff/start-session-settings`)
