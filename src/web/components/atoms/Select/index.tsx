import React, { SelectHTMLAttributes } from 'react';
import { selectStyle } from './style.css';

interface SelectProps extends SelectHTMLAttributes<HTMLSelectElement> {}

const Select: React.FC<SelectProps> = (props) => {
  return <select className={selectStyle} {...props} />;
};

export default Select;