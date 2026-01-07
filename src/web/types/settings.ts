import type { Hyperparameters } from './hyperparameters'

export type Settings = {
  apiMode: string
  contextLimit: number
  expertMode: boolean
  hyperparameters: Hyperparameters
  language: string
  maxToolCalls: number
  model: string
  referenceTtl: number
  searchModel: string
  sessionsPath: string
  timezone: string
  toolResponseExpiration: number
  yolo: boolean
}
