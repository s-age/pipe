import { JSX } from "react";
import { useController, UseControllerProps, FieldValues } from "react-hook-form";

import Checkbox from "@/components/atoms/Checkbox";
import Label from "@/components/atoms/Label";

import { checkboxContainer, labelStyle } from "./style.css";

type CheckboxFieldProps<TFieldValues extends FieldValues = FieldValues> = {
  label: string;
  id: string;
} & UseControllerProps<TFieldValues>;

const CheckboxField = <TFieldValues extends FieldValues = FieldValues>({
  label,
  id,
  ...props
}: CheckboxFieldProps<TFieldValues>): JSX.Element => {
  const { field } = useController(props);

  return (
    <div className={checkboxContainer}>
      <Checkbox
        id={id}
        checked={field.value}
        onChange={field.onChange}
        onBlur={field.onBlur}
        name={field.name}
      />
      <Label htmlFor={id} className={labelStyle}>
        {label}
      </Label>
    </div>
  );
};

export default CheckboxField;
