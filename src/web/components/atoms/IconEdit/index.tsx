import type { JSX } from 'react'

type IconProperties = {
  className?: string
  size?: number
}

const IconEdit = ({ className, size = 20 }: IconProperties): JSX.Element => (
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
  >
    <path d="M3 21v-3a2 2 0 0 1 .59-1.41L17.5 2.68a2 2 0 0 1 2.82 0l1 1a2 2 0 0 1 0 2.82L7.41 20.41A2 2 0 0 1 6 21H3z" />
    <path d="M14 7l3 3" />
  </svg>
)

export default IconEdit
