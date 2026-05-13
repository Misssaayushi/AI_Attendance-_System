import React from 'react';
import HomeHeader from '../components/home/HomeHeader';
import HeroSection from '../components/home/HeroSection';
import InfoSection from '../components/home/InfoSection';
import Container from '../components/Container';

const Home = () => {
  return (
    <div className="min-h-screen bg-gray-900 flex flex-col">
      <main className="flex-1">
        {/* Section 1: Header */}
        <HomeHeader />

        {/* Section 2: Hero & Action Buttons */}
        <HeroSection />

        {/* Section 3: Project Information Cards */}
        <InfoSection />
      </main>

      {/* Section 4: Footer */}
      <footer className="border-t border-gray-800 py-10 mt-auto">
        <Container>
          <div className="flex flex-col md:flex-row justify-between items-center gap-4 text-center md:text-left">
            <p className="text-gray-500 text-sm">
              &copy; 2026 AI Attendance Management System. All rights reserved.
            </p>
            <p className="text-gray-500 text-sm">
              Built for <span className="text-blue-500 font-medium">Your University Name</span>
            </p>
          </div>
        </Container>
      </footer>
    </div>
  );
};

export default Home;
