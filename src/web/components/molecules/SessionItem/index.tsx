import type { JSX } from 'react'

import { Checkbox } from '@/components/atoms/Checkbox'
import { Text } from '@/components/atoms/Text'
import { Box } from '@/components/molecules/Box'
import { Flex } from '@/components/molecules/Flex'
import { Grid } from '@/components/molecules/Grid'
import type {
  SessionOverview,
  SessionTreeNode
} from '@/lib/api/sessionTree/getSessionTree'

import { useSessionItemHandlers } from './hooks/useSessionItemHandlers'
import {
  sessionItem,
  label,
  checkbox,
  gridContent,
  subject,
  shortHash as shortHashStyle,
  createdAt
} from './style.css'

type Properties = {
  isSelected: boolean
  session: SessionOverview | SessionTreeNode
  updateLabel?: string
  useFilePath?: boolean
  onSelect: (sessionId: string, isSelected: boolean) => void
}

export const SessionItem = ({
  isSelected,
  session,
  updateLabel = 'Updated At',
  useFilePath = false,
  onSelect
}: Properties): JSX.Element => {
  const sessionId = session.sessionId || 'unknown'
  // Use filePath as identifier for archives to handle multiple versions
  const itemId =
    useFilePath && 'filePath' in session && session.filePath
      ? session.filePath
      : sessionId
  const sessionName =
    'purpose' in session
      ? session.purpose
      : (session.overview?.purpose as string) || 'Unknown'
  const displayDate =
    updateLabel === 'Deleted At'
      ? 'children' in session
        ? (session.overview?.deletedAt as string) || ''
        : session.deletedAt || ''
      : 'children' in session
        ? (session.overview?.lastUpdatedAt as string) || ''
        : session.lastUpdatedAt || ''

  const formatDate = (date: Date): string => {
    const year = date.getFullYear()
    const month = String(date.getMonth() + 1).padStart(2, '0')
    const day = String(date.getDate()).padStart(2, '0')
    const hours = String(date.getHours()).padStart(2, '0')
    const minutes = String(date.getMinutes()).padStart(2, '0')
    const seconds = String(date.getSeconds()).padStart(2, '0')

    return `${year}-${month}-${day} ${hours}:${minutes}:${seconds}`
  }

  const displayDateDate = displayDate ? new Date(displayDate) : null
  const displayDateDisplay =
    displayDateDate && !isNaN(displayDateDate.getTime())
      ? formatDate(displayDateDate)
      : 'Unknown'

  const shortHash = sessionId.slice(0, 7)

  const { handleSelect } = useSessionItemHandlers(itemId, isSelected, onSelect)

  return (
    <Box padding="s" className={sessionItem}>
      <Flex as="label" align="center" className={label}>
        <Checkbox
          id={`session-${itemId}`}
          className={checkbox}
          checked={isSelected}
          onChange={handleSelect}
        />
        <Grid columns="1fr 100px 180px" gap="s" className={gridContent}>
          <Text className={subject}>{sessionName}</Text>
          <Text className={shortHashStyle}>{shortHash}</Text>
          <Text className={createdAt}>{displayDateDisplay}</Text>
        </Grid>
      </Flex>
    </Box>
  )
}
