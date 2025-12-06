import type { Settings } from '@/types/settings'

import { client } from '../client'
import type { SessionOverview } from '../sessionTree/getSessionTree'

export type StartSessionSettingsResponse = {
  settings: Settings
  sessionTree: [string, SessionOverview][]
}

export const getStartSession = async (): Promise<StartSessionSettingsResponse> =>
  client.get<StartSessionSettingsResponse>('/bff/start_session')
