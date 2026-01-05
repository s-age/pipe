import { clsx } from 'clsx'
import type { JSX, ReactNode } from 'react'

import { code, pre } from './style.css'

type CodeProperties = {
  children?: ReactNode
  block?: boolean
  className?: string
}

export const Code = ({
  children,
  block = false,
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
