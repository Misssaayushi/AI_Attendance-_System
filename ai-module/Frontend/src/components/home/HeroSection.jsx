import React from 'react';
import { useNavigate } from 'react-router-dom';
import { Fingerprint } from 'lucide-react';
import Button from '../Button';
import Container from '../Container';

const HeroSection = () => {
  const navigate = useNavigate();

  return (
    <section className="py-12 sm:py-16 text-center">
      <Container className="flex flex-col items-center">
        <div className="p-5 bg-blue-600/20 rounded-full mb-8">
          <Fingerprint size={72} className="text-blue-500" />
        </div>
        
        <p className="text-lg text-gray-400 max-w-2xl mb-10">
          Smart, secure, and automated attendance tracking leveraging facial recognition 
          technology for a seamless university experience.
        </p>

        <div className="flex flex-col sm:flex-row gap-4 justify-center">
          <Button 
            size="lg" 
            onClick={() => navigate('/attendance')}
            className="w-full sm:w-auto"
          >
            Start Attendance
          </Button>
          <Button 
            size="lg" 
            variant="outline" 
            onClick={() => navigate('/register')}
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
