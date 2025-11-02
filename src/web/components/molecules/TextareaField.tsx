import { useController, UseControllerProps, FieldValues } from 'react-hook-form';
import Label from '@/components/atoms/Label';
import TextArea from '@/components/atoms/TextArea';
import { errorMessageStyle } from './TextareaField.css';

interface TextareaFieldProps<TFieldValues extends FieldValues = FieldValues> extends UseControllerProps<TFieldValues> {
  label: string;
  id: string;
  placeholder?: string;
  readOnly?: boolean;
  required?: boolean;
}

const TextareaField = <TFieldValues extends FieldValues = FieldValues>({ label, id, placeholder, readOnly, required, ...props }: TextareaFieldProps<TFieldValues>) => {
  const { field, fieldState: { error } } = useController(props);

  return (
    <div>
      <Label htmlFor={id}>{label}</Label>
      <TextArea id={id} placeholder={placeholder} readOnly={readOnly} required={required} {...field} />
      {error && <p className={errorMessageStyle}>{error.message}</p>}
    </div>
  );
};

export default TextareaField;