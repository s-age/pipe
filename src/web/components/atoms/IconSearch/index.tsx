import type { JSX, SVGAttributes } from 'react'

type IconProperties = {
  size?: number
} & SVGAttributes<SVGSVGElement>

export const IconSearch = ({
  size = 20,
  className,
  ...properties
}: IconProperties): JSX.Element => (
  <svg
    xmlns="http://www.w3.org/2000/svg"
    width={size}
    height={size}
    viewBox="0 0 24 24"
    fill="none"
    stroke="currentColor"
    strokeWidth="1.8"
    strokeLinecap="round"
    strokeLinejoin="round"
    className={className}
    aria-hidden="true"
    focusable="false"
    {...properties}
  >
    <circle cx="11" cy="11" r="6" />
    <path d="M21 21l-4.35-4.35" />
  </svg>
)
