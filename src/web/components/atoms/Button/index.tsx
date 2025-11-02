import { ButtonHTMLAttributes, JSX } from 'react';
import { button } from './style.css';
import clsx from 'clsx';

interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  kind?: 'primary' | 'secondary' | 'ghost';
  size?: 'small' | 'default' | 'large' | 'xsmall';
  text?: 'bold' | 'uppercase';
  hasBorder?: boolean;
}

const Button: (props: ButtonProps) => JSX.Element = ({ kind = 'primary', size = 'default', text, hasBorder = true, className, ...props }) => {
  return <button className={clsx(button({ kind, size, text, hasBorder }), className)} {...props} />;
};

export default Button;