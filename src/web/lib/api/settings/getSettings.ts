import { Hyperparameters } from '@/types/hyperparameters'

import { client } from '../client'

export type Settings = {
  parameters: Hyperparameters
}

export const getSettings = async (): Promise<Settings> => {
  const data = await client.get<{ settings: Settings }>(`/settings`)

  return data.settings
}
