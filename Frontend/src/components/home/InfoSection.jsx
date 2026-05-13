import React from 'react';
import { Zap, ShieldCheck, BarChart3 } from 'lucide-react';
import Container from '../Container';
import InfoCard from './InfoCard';

const InfoSection = () => {
  const benefits = [
    {
      icon: Zap,
      title: "AI-Powered Recognition",
      description: "Leverages OpenCV-based facial recognition for instant, contactless attendance marking with high accuracy.",
      iconColorClass: "text-blue-400",
      iconBgClass: "bg-blue-500/20"
    },
    {
      icon: ShieldCheck,
      title: "Secure & Reliable",
      description: "Tamper-proof records stored in a MySQL database with real-time sync and secure audit trails for every entry.",
      iconColorClass: "text-green-400",
      iconBgClass: "bg-green-500/20"
    },
    {
      icon: BarChart3,
      title: "Real-Time Analytics",
      description: "Live dashboard with attendance trends, late arrival tracking, and comprehensive exportable reports.",
      iconColorClass: "text-violet-400",
      iconBgClass: "bg-violet-500/20"
    }
  ];

  return (
    <section className="py-12 sm:py-16">
      <Container>
        <h2 className="text-2xl sm:text-3xl font-bold text-white text-center mb-12">
          Why AI Attendance?
        </h2>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-8">
          {benefits.map((benefit, index) => (
            <InfoCard key={index} {...benefit} />
          ))}
        </div>
      </Container>
    </section>
  );
};

export default InfoSection;
