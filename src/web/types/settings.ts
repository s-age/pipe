import type { Hyperparameters } from './hyperparameters'

export type Settings = {
  model: string
  search_model: string
  context_limit: number
  api_mode: string
  language: string
  yolo: boolean
  max_tool_calls: number
  hyperparameters: Hyperparameters
  expert_mode: boolean
  sessions_path: string
  reference_ttl: number
  tool_response_expiration: number
  timezone: string
}
