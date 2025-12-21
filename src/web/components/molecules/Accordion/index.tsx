import { clsx } from 'clsx'
import { type JSX, type ReactNode } from 'react'

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
  id?: string
  title: string | JSX.Element
  summary?: string | JSX.Element
  defaultOpen?: boolean
  open?: boolean
  onOpenChange?: (open: boolean) => void
  children?: ReactNode
  className?: string
}

export const Accordion = ({
  id,
  title,
  summary,
  defaultOpen = false,
  open: controlledOpen,
  onOpenChange,
  children,
  className
}: AccordionProperties): JSX.Element => {
  const { open, contentId, handleToggle, handleKeyDown } = useAccordion({
    id,
    defaultOpen,
    controlledOpen,
    onOpenChange
  })

  return (
    <div className={clsx(accordionRoot, className)}>
      <div
        className={header}
        role="button"
        tabIndex={0}
        onClick={handleToggle}
        onKeyDown={handleKeyDown}
        aria-expanded={open}
        aria-controls={contentId}
      >
        <div className={headerLeft}>
          <div className={titleStyle}>{title}</div>
          {summary ? <div className={summaryStyle}>{summary}</div> : null}
        </div>
        <div aria-hidden={true} className={clsx(chevron, open && chevronOpen)}>
          ▸
        </div>
      </div>

      {open && (
        <div id={contentId} className={contentStyle} role="region">
          {children}
        </div>
      )}
    </div>
  )
}
