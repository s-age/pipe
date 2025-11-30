export type Diagnosis = {
  deletions: number[]
  edits: { turn: number; suggestion: string }[]
  compressions: { start: number; end: number; reason: string }[]
}
