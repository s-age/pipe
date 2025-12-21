import type { JSX } from 'react'

import { Button } from '@/components/atoms/Button'

import { turnContent, editTextArea, editButtonContainer } from './style.css'

type EditingContentProperties = {
  editedContent: string
  onEditedChange?: (event: React.ChangeEvent<HTMLTextAreaElement>) => void
  onSaveEdit?: () => void
  onCancelEdit?: () => void
}

export const EditingContent = ({
  editedContent,
  onEditedChange,
  onSaveEdit,
  onCancelEdit
}: EditingContentProperties): JSX.Element => (
  <div className={turnContent}>
    <textarea
      className={editTextArea}
      value={editedContent}
      onChange={onEditedChange}
    />
    <div className={editButtonContainer}>
      <Button kind="primary" size="default" onClick={onSaveEdit}>
        Save
      </Button>
      <Button kind="secondary" size="default" onClick={onCancelEdit}>
        Cancel
      </Button>
    </div>
  </div>
)
