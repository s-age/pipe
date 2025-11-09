import type { JSX } from 'react'

import { InputSearch } from '@/components/molecules/InputSearch'

import { headerContainer, headerTitle, searchWrapper } from './style.css'

export const Header = (): JSX.Element => (
  <header className={headerContainer}>
    <div className={headerTitle}>Pipe</div>
    <div className={searchWrapper}>
      <InputSearch />
    </div>
  </header>
)
