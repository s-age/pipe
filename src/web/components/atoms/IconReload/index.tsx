import type { JSX, SVGAttributes } from 'react'

type IconProperties = {
  size?: number
} & SVGAttributes<SVGSVGElement>

export const IconReload = ({
  className,
  size = 20,
  ...properties
}: IconProperties): JSX.Element => (
  <svg
    xmlns="http://www.w3.org/2000/svg"
    width={size}
    height={size}
    viewBox="0 0 24 24"
    fill="none"
    stroke="currentColor"
    strokeWidth="1.5"
    strokeLinecap="round"
    strokeLinejoin="round"
    className={className}
    aria-hidden="true"
    focusable="false"
    {...properties}
  >
    <path d="M21 12a9 9 0 1 1-3-6.7" />
    <polyline points="21 3 21 9 15 9" />
  </svg>
)

// Default export removed — use named export `IconReload`
