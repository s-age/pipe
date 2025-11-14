import clsx from 'clsx'
import type { HTMLAttributes, JSX } from 'react'

import { loadingSpinnerStyle } from './style.css'

type LoadingSpinnerProperties = {} & HTMLAttributes<HTMLDivElement>

export const LoadingSpinner = ({
  className,
  ...properties
}: LoadingSpinnerProperties): JSX.Element => (
  <div className={clsx(loadingSpinnerStyle, className)} {...properties}>
    Loading...
  </div>
)

// (Removed temporary default export) Use named export `LoadingSpinner`.
