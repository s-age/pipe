import type { JSX } from 'react'

import { loadingSpinnerStyle } from './style.css'

export const LoadingSpinner: () => JSX.Element = () => (
  <div className={loadingSpinnerStyle}>Loading...</div>
)

// (Removed temporary default export) Use named export `LoadingSpinner`.
