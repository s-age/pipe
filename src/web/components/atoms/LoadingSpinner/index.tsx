import { JSX } from 'react'

import { loadingSpinnerStyle } from './style.css'

const LoadingSpinner: () => JSX.Element = () => (
  <div className={loadingSpinnerStyle}>Loading...</div>
)

export default LoadingSpinner
