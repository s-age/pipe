import type { JSX, HTMLAttributes, ReactNode } from 'react'

import { legendStyle, visuallyHidden } from './style.css'

type LegendProperties = HTMLAttributes<HTMLLegendElement> & {
  children: ReactNode
  visuallyHidden?: boolean
}

const Legend = ({
  children,
  visuallyHidden: hide = false,
  ...rest
}: LegendProperties): JSX.Element => (
  <legend className={hide ? visuallyHidden : legendStyle} {...rest}>
    {children}
  </legend>
)

export default Legend
