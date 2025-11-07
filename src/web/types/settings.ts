import { Hyperparameters } from './hyperparameters'

export type Settings = {
  parameters: Hyperparameters
  [key: string]: unknown
}
