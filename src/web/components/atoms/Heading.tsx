import React, { HTMLAttributes } from 'react';
import { h1Style } from './Heading.css';

interface HeadingProps extends HTMLAttributes<HTMLHeadingElement> {
  level?: 1 | 2 | 3 | 4 | 5 | 6;
}

const Heading: React.FC<HeadingProps> = ({ level = 1, children, className, ...props }) => {
  const Tag = `h${level}`;
  const headingClassName = `${level === 1 ? h1Style : ''} ${className || ''}`.trim();
  return React.createElement(Tag, { className: headingClassName, ...props }, children);
};

export default Heading;