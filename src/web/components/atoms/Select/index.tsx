import type { SelectHTMLAttributes, JSX } from 'react'

import { selectStyle } from './style.css'

type SelectProperties = {} & SelectHTMLAttributes<HTMLSelectElement>

const Select: (properties: SelectProperties) => JSX.Element = (properties) => (
  <select className={selectStyle} {...properties} />
)

export default Select
