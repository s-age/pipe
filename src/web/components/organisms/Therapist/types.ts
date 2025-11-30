export type Diagnosis = {
  deletions: number[]
  edits: { turn: number; new_content: string }[]
  compressions: { start: number; end: number; reason: string }[]
  summary: string
  raw_diagnosis?: string
}
