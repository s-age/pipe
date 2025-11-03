import { SelectHTMLAttributes, JSX } from "react";

import { selectStyle } from "./style.css";

type SelectProps = {} & SelectHTMLAttributes<HTMLSelectElement>;

const Select: (props: SelectProps) => JSX.Element = (props) => (
  <select className={selectStyle} {...props} />
);

export default Select;
