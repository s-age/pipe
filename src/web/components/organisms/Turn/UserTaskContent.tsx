import type { JSX } from 'react'

import { editablePre } from './style.css'

type UserTaskContentProperties = {
  instruction: string
}

export const UserTaskContent = ({
  instruction
}: UserTaskContentProperties): JSX.Element => (
  <pre className={editablePre}>{instruction || ''}</pre>
)
