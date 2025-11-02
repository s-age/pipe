import { useController, UseControllerProps, FieldValues } from 'react-hook-form';
import Checkbox from '@/components/atoms/Checkbox';
import Label from '@/components/atoms/Label';
import { checkboxContainer, labelStyle } from './CheckboxField.css';

interface CheckboxFieldProps<TFieldValues extends FieldValues = FieldValues> extends UseControllerProps<TFieldValues> {
  label: string;
  id: string;
}

const CheckboxField = <TFieldValues extends FieldValues = FieldValues>({ label, id, ...props }: CheckboxFieldProps<TFieldValues>) => {
  const { field } = useController(props);

  return (
    <div className={checkboxContainer}>
      <Checkbox id={id} checked={field.value} onChange={field.onChange} onBlur={field.onBlur} name={field.name} />
      <Label htmlFor={id} className={labelStyle}>{label}</Label>
    </div>
  );
};

export default CheckboxField;