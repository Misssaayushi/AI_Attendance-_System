import React from 'react';
import Container from '../Container';

const HomeHeader = () => {
  return (
    <header className="pt-16 pb-8 text-center">
      <Container>
        <p className="text-sm font-semibold uppercase tracking-widest text-blue-400 mb-2">
          Your University Name
        </p>
        <h1 className="text-3xl sm:text-4xl lg:text-5xl font-bold text-white mb-6">
          AI Attendance Management System
        </h1>
        <div className="h-1 w-24 bg-gradient-to-r from-blue-500 to-violet-500 mx-auto rounded-full"></div>
      </Container>
    </header>
  );
};

export default HomeHeader;
