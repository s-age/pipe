import React, { TextareaHTMLAttributes } from 'react';
import { textareaStyle } from './TextArea.css';

interface TextAreaProps extends TextareaHTMLAttributes<HTMLTextAreaElement> {}

const TextArea: React.FC<TextAreaProps> = (props) => {
  return <textarea className={textareaStyle} {...props} />;
};

export default TextArea;