import React, { LabelHTMLAttributes } from 'react';
import { labelStyle } from './style.css';

interface LabelProps extends LabelHTMLAttributes<HTMLLabelElement> {}

const Label: React.FC<LabelProps> = (props) => {
  return <label className={labelStyle} {...props} />;
};

export default Label;