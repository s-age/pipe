import { TextareaHTMLAttributes, JSX } from 'react';
import { textareaStyle } from './style.css';

interface TextAreaProps extends TextareaHTMLAttributes<HTMLTextAreaElement> {}

const TextArea: (props: TextAreaProps) => JSX.Element = (props) => {
  return <textarea className={textareaStyle} {...props} />;
};

export default TextArea;