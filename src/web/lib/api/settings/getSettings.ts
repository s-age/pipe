import type { Settings } from '@/types/settings'

import { client } from '../client'

export const getSettings = async (): Promise<Settings> => {
  const data = await client.get<{ settings: Settings }>('/settings')

  return data.settings
}
