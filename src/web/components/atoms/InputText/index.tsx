import { InputHTMLAttributes, JSX } from 'react';
import { inputStyle } from './style.css';

interface InputTextProps extends InputHTMLAttributes<HTMLInputElement> {}

const InputText: (props: InputTextProps) => JSX.Element = (props) => {
  return <input type="text" className={inputStyle} {...props} />;
};

export default InputText;