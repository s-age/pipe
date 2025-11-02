import React, { InputHTMLAttributes } from 'react';
import { checkboxStyle } from './Checkbox.css';

interface CheckboxProps extends InputHTMLAttributes<HTMLInputElement> {}

const Checkbox: React.FC<CheckboxProps> = (props) => {
  return <input type="checkbox" className={checkboxStyle} {...props} />;
};

export default Checkbox;