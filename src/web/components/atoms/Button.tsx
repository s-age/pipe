import React, { ButtonHTMLAttributes } from 'react';
import { baseButtonStyle, cancelButton } from './Button.css';

interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'cancel';
}

const Button: React.FC<ButtonProps> = ({ variant = 'primary', className, ...props }) => {
  const buttonClassName = `${baseButtonStyle} ${variant === 'cancel' ? cancelButton : ''} ${className || ''}`.trim();
  return <button className={buttonClassName} {...props} />;
};

export default Button;