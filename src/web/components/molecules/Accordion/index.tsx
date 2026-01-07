import { clsx } from 'clsx'
import { type JSX, type ReactNode } from 'react'

import { Box } from '@/components/molecules/Box'
import { Flex } from '@/components/molecules/Flex'
import { FlexColumn } from '@/components/molecules/FlexColumn'

import { useAccordion } from './hooks/useAccordion'
import {
  accordionRoot,
  header,
  headerLeft,
  title as titleStyle,
  summary as summaryStyle,
  chevron,
  chevronOpen,
  content as contentStyle
} from './style.css'

type AccordionProperties = {
  title: string | JSX.Element
  children?: ReactNode
  className?: string
  defaultOpen?: boolean
  id?: string
  open?: boolean
  summary?: string | JSX.Element
  onOpenChange?: (open: boolean) => void
}

export const Accordion = ({
  title,
  children,
  className,
  defaultOpen = false,
  id,
  open: controlledOpen,
  summary,
  onOpenChange
}: AccordionProperties): JSX.Element => {
  const { contentId, handleKeyDown, handleToggle, open } = useAccordion({
    id,
    defaultOpen,
    controlledOpen,
    onOpenChange
  })

  return (
    <FlexColumn className={clsx(accordionRoot, className)}>
      <Flex
        className={header}
        role="button"
        tabIndex={0}
        onClick={handleToggle}
        onKeyDown={handleKeyDown}
        aria-expanded={open}
        aria-controls={contentId}
      >
        <Flex className={headerLeft}>
          <Box className={titleStyle}>{title}</Box>
          {summary ? <Box className={summaryStyle}>{summary}</Box> : null}
        </Flex>
        <Box aria-hidden={true} className={clsx(chevron, open && chevronOpen)}>
          ▸
        </Box>
      </Flex>

      {open && (
        <Box id={contentId} className={contentStyle} role="region">
          {children}
        </Box>
      )}
    </FlexColumn>
  )
}
