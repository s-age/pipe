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
