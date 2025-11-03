import { InputHTMLAttributes, JSX } from "react";

import { checkboxStyle } from "./style.css";

type CheckboxProps = {} & InputHTMLAttributes<HTMLInputElement>;

const Checkbox: (props: CheckboxProps) => JSX.Element = (props) => (
  <input type="checkbox" className={checkboxStyle} {...props} />
);

export default Checkbox;
