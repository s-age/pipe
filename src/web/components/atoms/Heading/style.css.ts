import { recipe } from '@vanilla-extract/recipes'

import { colors } from '../../../styles/colors.css'

export const heading = recipe({
  base: {
    color: colors.cyan
  },
  variants: {
    level: {
      1: {
        borderBottom: `1px solid ${colors.gray}`,
        paddingBottom: '12px',
        marginBottom: '20px'
      },
      2: {},
      3: {},
      4: {},
      5: {},
      6: {}
    }
  },
  defaultVariants: {
    level: 1
  }
})
