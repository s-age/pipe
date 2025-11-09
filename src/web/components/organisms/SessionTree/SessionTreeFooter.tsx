import type { JSX } from 'react'

import { Button } from '@/components/atoms/Button'

import { stickyNewChatButtonContainer } from './style.css'

type SessionTreeFooterProperties = {
  handleNewChatClick: () => void
}

export const SessionTreeFooter = ({
  handleNewChatClick
}: SessionTreeFooterProperties): JSX.Element => (
  <div className={stickyNewChatButtonContainer}>
    <Button kind="primary" size="default" onClick={handleNewChatClick}>
      + New Chat
    </Button>
  </div>
)
