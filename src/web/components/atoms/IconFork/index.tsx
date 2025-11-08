import type { JSX } from 'react'

type IconProperties = {
  className?: string
  size?: number
}

const IconFork = ({ className, size = 20 }: IconProperties): JSX.Element => (
  <svg
    xmlns="http://www.w3.org/2000/svg"
    width={size}
    height={size}
    viewBox="0 0 24 24"
    fill="none"
    stroke="currentColor"
    strokeWidth="1.6"
    strokeLinecap="round"
    strokeLinejoin="round"
    className={className}
    aria-hidden="true"
    focusable="false"
  >
    {/* Top-left node */}
    <circle cx="6" cy="6" r="2" />
    {/* Top-right node */}
    <circle cx="18" cy="6" r="2" />
    {/* Bottom node */}
    <circle cx="12" cy="18" r="2" />

    {/* Branch lines: top nodes connect to junction, then down to bottom node */}
    <path d="M6 8.5 L12 12 L18 8.5" />
    <path d="M12 12 L12 16" />
  </svg>
)

export default IconFork
