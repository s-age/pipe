import { SelectHTMLAttributes, JSX } from 'react';
import { selectStyle } from './style.css';

interface SelectProps extends SelectHTMLAttributes<HTMLSelectElement> {}

const Select: (props: SelectProps) => JSX.Element = (props) => {
  return <select className={selectStyle} {...props} />;
};

export default Select;