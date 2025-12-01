import type { ReactNode } from 'react'

import { Header } from '@/components/organisms/Header'

import { appContainer } from './style.css.ts'

export const AppLayout = ({ children }: { children: ReactNode }) => {
  return (
    <div className={appContainer}>
      <Header />
      {children}
    </div>
  )
}
