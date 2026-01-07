import type { JSX, SVGAttributes } from 'react'

type IconProperties = {
  size?: number
} & SVGAttributes<SVGSVGElement>

export const IconPaperPlane = ({
  className,
  size = 24,
  ...properties
}: IconProperties): JSX.Element => (
  <svg
    xmlns="http://www.w3.org/2000/svg"
    width={size}
    height={size}
    viewBox="0 0 48 48"
    fill="none"
    stroke="currentColor"
    strokeWidth="4"
    strokeLinecap="round"
    strokeLinejoin="round"
    className={className}
    aria-hidden="true"
    focusable="false"
    {...properties}
  >
    <path d="M44 4L22 26" />
    <path d="M44 4l-14 40-8-18-18-8 40-14z" />
  </svg>
)

// Default export removed — use named export `IconPaperPlane`
