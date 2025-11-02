import { style } from '@vanilla-extract/css';
import { colors } from '../../../styles/colors.css';

export const pageContainer = style({
  fontFamily: 'Segoe UI, Tahoma, Geneva, Verdana, sans-serif',
  margin: '0',
  backgroundColor: colors.mediumBackground,
  color: colors.darkBackground,
  padding: '16px',
});

export const errorMessageStyle = style({
  color: colors.error,
  marginTop: '10px',
  textAlign: 'center',
});
