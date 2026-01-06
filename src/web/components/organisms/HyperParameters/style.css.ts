import { style } from '@vanilla-extract/css'

export const hyperparametersControl = style({
  marginBottom: '10px'
})

export const labelContainer = style({
  // Use percentage so layout adapts to the container width and avoids overflow.
  // Keep a fixed proportion for labels so they align vertically.
  flex: '0 0 35%',
  textAlign: 'left'
})

export const sliderContainer = style({
  // Slider takes the remaining space; set a modest minWidth to avoid collapse.
  flex: '1 1 65%',
  minWidth: '80px'
})

export const note = style({
  marginTop: '8px',
  fontSize: 'small',
  color: 'gray',
  opacity: 0.7
})
