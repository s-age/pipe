import type { JSX } from 'react'

import { Button } from '@/components/atoms/Button'
import { Box } from '@/components/molecules/Box'

import { stickyNewChatButtonContainer, newChatButton } from './style.css'

type SessionTreeFooterProperties = {
  handleNewChatClick: () => void
}

export const SessionTreeFooter = ({
  handleNewChatClick
}: SessionTreeFooterProperties): JSX.Element => (
  <Box className={stickyNewChatButtonContainer}>
    <Button
      kind="primary"
      size="default"
      onClick={handleNewChatClick}
      className={newChatButton}
      aria-label="New Chat"
    >
      + New Chat
    </Button>
  </Box>
)
