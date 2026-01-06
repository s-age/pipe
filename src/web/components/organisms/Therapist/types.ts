export type Diagnosis = {
  compressions: { end: number; reason: string; start: number }[]
  deletions: number[]
  edits: { newContent: string; turn: number }[]
  summary: string
  rawDiagnosis?: string
}
