import { recipe } from '@vanilla-extract/recipes';
import { colors } from '../../../styles/colors.css';

export const button = recipe({
  base: {
    border: 'none !important',
    fontSize: '1em',
    borderRadius: '4px',
    cursor: 'pointer',
    transition: 'background-color 0.2s',
  },
  variants: {
    kind: {
      primary: {
        backgroundColor: colors.accent,
        color: colors.darkBackground,
        ':hover': {
          backgroundColor: colors.accentHover,
        },
      },
      secondary: {
        backgroundColor: colors.mediumBackground,
        color: colors.lightText,
        ':hover': {
          backgroundColor: colors.accent,
        },
      },
      ghost: {
        backgroundColor: 'transparent',
        opacity: 0.85,
        color: colors.lightText,
        ':hover': {
          backgroundColor: 'transparent',
          opacity: 1,
        },
      },
    },
    size: {
      small: {
        padding: '4px 20px',
      },
      default: {
        padding: '8px 20px',
      },
      large: {
        padding: '12px 20px',
      },
      xsmall: {
        padding: '4px 4px',
        minWidth: '16px',
      },
    },
    text: {
      bold: {
        fontWeight: 'bold',
      },
      uppercase: {
        textTransform: 'uppercase',
      },
    },
    hasBorder: {
      true: {
        border: '1px solid currentColor',
      },
      false: {
        border: 'none !important',
        background: 'transparent',
      },
    },
  },
  defaultVariants: {
    kind: 'primary',
    size: 'default',
    hasBorder: true,
  },
});