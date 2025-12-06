import type { Hyperparameters } from './hyperparameters'

export type Settings = {
  model: string
  searchModel: string
  contextLimit: number
  apiMode: string
  language: string
  yolo: boolean
  maxToolCalls: number
  hyperparameters: Hyperparameters
  expertMode: boolean
  sessionsPath: string
  referenceTtl: number
  toolResponseExpiration: number
  timezone: string
}
