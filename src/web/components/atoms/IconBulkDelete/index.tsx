import type { JSX, SVGAttributes } from 'react'

type IconProperties = {
  size?: number
} & SVGAttributes<SVGSVGElement>

export const IconBulkDelete = ({
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
    strokeWidth="1.5"
    strokeLinecap="round"
    strokeLinejoin="round"
    className={className}
    aria-hidden="true"
    focusable="false"
    {...properties}
  >
    {/* Back stacked items (indicate multiple) */}
    <rect x="3" y="7" width="10" height="10" rx="2" />
    <rect x="7" y="3" width="12" height="12" rx="2" />

    {/* Trash can in front */}
    <polyline points="9 7 9 5 15 5 15 7" />
    <path d="M19 7l-1 12a2 2 0 0 1-2 2H8a2 2 0 0 1-2-2L5 7" />
    <line x1="10" y1="11" x2="10" y2="17" />
    <line x1="14" y1="11" x2="14" y2="17" />
  </svg>
)
