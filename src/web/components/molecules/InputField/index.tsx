import { useController, UseControllerProps, FieldValues } from 'react-hook-form';
import InputText from '@/components/atoms/InputText';
import Label from '@/components/atoms/Label';
import { errorMessageStyle, inputFieldStyle } from './style.css';

interface InputFieldProps<TFieldValues extends FieldValues = FieldValues> extends UseControllerProps<TFieldValues> {
  label: string;
  id: string;
  type?: string;
  placeholder?: string;
  required?: boolean;
  min?: string;
  max?: string;
  step?: string;
}

const InputField = <TFieldValues extends FieldValues = FieldValues>({ label, id, type = 'text', placeholder, required, min, max, step, ...props }: InputFieldProps<TFieldValues>) => {
  const { field, fieldState: { error } } = useController(props);

  return (
    <div>
      <Label htmlFor={id}>{label}</Label>
      <InputText id={id} type={type} className={inputFieldStyle} placeholder={placeholder} required={required} min={min} max={max} step={step} {...field} />
      {error && <p className={errorMessageStyle}>{error.message}</p>}
    </div>
  );
};

export default InputField;