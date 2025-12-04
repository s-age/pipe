import type { ReactNode, JSX } from 'react'

import { Header } from '@/components/organisms/Header'

import { appContainer } from './style.css.ts'

export const AppLayout = ({ children }: { children: ReactNode }): JSX.Element => (
  <div className={appContainer}>
    <Header />
    {children}
  </div>
)
