import type { JSX } from 'react'

type IconProperties = {
  className?: string
  size?: number
}

export const IconDelete = ({ className, size = 20 }: IconProperties): JSX.Element => (
  <svg
    xmlns="http://www.w3.org/2000/svg"
    width={size}
    height={size}
    viewBox="0 0 48 48"
    fill="currentColor"
    className={className}
    aria-hidden="true"
    focusable="false"
  >
    {/* Lid */}
    <rect x="3.8" y="4" width="42.0" height="4.4" rx="0.9" />
    {/* Lid handle (small rounded rectangle centered on lid) */}
    <rect x="22.0" y="0" width="4.8" height="4.0" rx="0.48" />
    {/* Body (narrower, with a small gap under the lid) */}
    <rect x="8.5" y="10" width="32" height="32" rx="4" />
  </svg>
)

// Default export removed — use named export `IconDelete`
