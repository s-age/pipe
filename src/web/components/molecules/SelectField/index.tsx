import { useController, UseControllerProps, FieldValues } from 'react-hook-form';
import Select from '@/components/atoms/Select';
import Label from '@/components/atoms/Label';
import { errorMessageStyle } from './style.css';
import { JSX } from 'react';

interface SelectOption {
  value: string;
  label: string;
}

interface SelectFieldProps<TFieldValues extends FieldValues = FieldValues> extends UseControllerProps<TFieldValues> {
  label: string;
  id: string;
  options: SelectOption[];
}

const SelectField = <TFieldValues extends FieldValues = FieldValues>({ label, id, options, ...props }: SelectFieldProps<TFieldValues>): JSX.Element => {
  const { field, fieldState: { error } } = useController(props);

  return (
    <div>
      <Label htmlFor={id}>{label}</Label>
      <Select id={id} {...field}>
        {options.map((option) => (
          <option key={option.value} value={option.value}>
            {option.label}
          </option>
        ))}
      </Select>
      {error && <p className={errorMessageStyle}>{error.message}</p>}
    </div>
  );
};

export default SelectField;