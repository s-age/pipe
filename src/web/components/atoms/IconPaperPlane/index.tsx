import type { JSX } from 'react'

type IconProperties = {
  className?: string
  size?: number
}

const IconPaperPlane = ({ className, size = 24 }: IconProperties): JSX.Element => (
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
  >
    <path d="M44 4L22 26" />
    <path d="M44 4l-14 40-8-18-18-8 40-14z" />
  </svg>
)

export default IconPaperPlane
