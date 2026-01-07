import type { JSX } from 'react'

import { Code } from '@/components/molecules/Code'

import { editablePre } from './style.css'

type UserTaskContentProperties = {
  instruction: string
}

export const UserTaskContent = ({
  instruction
}: UserTaskContentProperties): JSX.Element => (
  <Code block={true} className={editablePre}>
    {instruction || ''}
  </Code>
)
