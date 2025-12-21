import type { Settings } from '@/types/settings'

import { client } from '../client'
import type { SessionTreeNode } from '../sessionTree/getSessionTree'

export type StartSessionSettingsResponse = {
  settings: Settings
  sessionTree: SessionTreeNode[]
}

export const getStartSession = async (): Promise<StartSessionSettingsResponse> =>
  client.get<StartSessionSettingsResponse>('/bff/start_session')
