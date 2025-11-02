import React, { InputHTMLAttributes } from 'react';
import { inputStyle } from './style.css';

interface InputTextProps extends InputHTMLAttributes<HTMLInputElement> {}

const InputText: React.FC<InputTextProps> = (props) => {
  return <input type="text" className={inputStyle} {...props} />;
};

export default InputText;