import { LabelHTMLAttributes, JSX } from 'react';
import { labelStyle } from './style.css';

interface LabelProps extends LabelHTMLAttributes<HTMLLabelElement> {}

const Label: (props: LabelProps) => JSX.Element = (props) => {
  return <label className={labelStyle} {...props} />;
};

export default Label;