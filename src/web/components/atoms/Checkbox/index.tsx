import { InputHTMLAttributes, JSX } from 'react';
import { checkboxStyle } from './style.css';

interface CheckboxProps extends InputHTMLAttributes<HTMLInputElement> {}

const Checkbox: (props: CheckboxProps) => JSX.Element = (props) => {
  return <input type="checkbox" className={checkboxStyle} {...props} />;
};

export default Checkbox;