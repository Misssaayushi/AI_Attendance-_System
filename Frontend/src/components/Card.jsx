import React from 'react';

const Card = ({ children, className = '' }) => {
  return (
    <div className={`bg-gray-800 rounded-lg shadow-lg border border-gray-700 p-6 ${className}`}>
      {children}
    </div>
  );
};

export default Card;
