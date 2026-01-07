import { clsx } from 'clsx'
import type { JSX, ReactNode } from 'react'

import { code, pre } from './style.css'

type CodeProperties = {
  block?: boolean
  children?: ReactNode
  className?: string
}

export const Code = ({
  block = false,
  children,
  className,
  ...rest
}: CodeProperties): JSX.Element => {
  if (block) {
    return (
      <pre className={clsx(pre, className)} {...rest}>
        <code>{children}</code>
      </pre>
    )
  }

  return (
    <code className={clsx(code, className)} {...rest}>
      {children}
    </code>
  )
}
