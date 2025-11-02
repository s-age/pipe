import React, { SelectHTMLAttributes } from 'react';
import { selectStyle } from './Select.css';

interface SelectProps extends SelectHTMLAttributes<HTMLSelectElement> {}

const Select: React.FC<SelectProps> = (props) => {
  return <select className={selectStyle} {...props} />;
};

export default Select;