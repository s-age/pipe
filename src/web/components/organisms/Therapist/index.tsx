import type { JSX } from 'react'

import * as styles from './style.css'

export const Therapist = (): JSX.Element => (
  <div className={styles.container}>
    <div className={styles.body}>
      <h4 className={styles.title}>Therapist</h4>
      <p className={styles.muted}>Therapist agent placeholder (empty)</p>
    </div>
  </div>
)
