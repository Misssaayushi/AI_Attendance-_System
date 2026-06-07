import React from 'react';
import { useNavigate } from 'react-router-dom';
import Button from '../Button';
import Container from '../Container';

const HeroSection = () => {
  const navigate = useNavigate();

  return (
    <section className="py-12 sm:py-16 text-center">
      <Container className="flex flex-col items-center">
        <p className="text-lg text-gray-400 max-w-2xl mb-10">
          Smart, secure, and automated attendance tracking leveraging facial recognition 
          technology for a seamless university experience.
        </p>

        <div className="flex flex-col sm:flex-row gap-4 justify-center">
          <Button 
            type="button"
            size="lg" 
            onClick={(e) => { e.preventDefault(); navigate('/attendance'); }}
            className="w-full sm:w-auto"
          >
            Start Attendance
          </Button>
          <Button 
            type="button"
            size="lg" 
            variant="outline" 
            onClick={(e) => { e.preventDefault(); navigate('/register'); }}
            className="w-full sm:w-auto"
          >
            Register New User
          </Button>
        </div>
      </Container>
    </section>
  );
};

export default HeroSection;
