export type Diagnosis = {
  deletions: number[]
  edits: { turn: number; newContent: string }[]
  compressions: { start: number; end: number; reason: string }[]
  summary: string
  rawDiagnosis?: string
}
