import React from 'react';
import Card from '../Card';

const InfoCard = ({ icon: Icon, title, description, iconColorClass = 'text-blue-400', iconBgClass = 'bg-blue-500/20' }) => {
  return (
    <Card className="flex flex-col items-center text-center p-8 h-full transition-transform hover:scale-[1.02]">
      <div className={`p-3 rounded-full ${iconBgClass} ${iconColorClass} mb-4`}>
        <Icon size={28} />
      </div>
      <h3 className="text-xl font-semibold text-white mb-3">{title}</h3>
      <p className="text-gray-400 text-sm leading-relaxed">
        {description}
      </p>
    </Card>
  );
};

export default InfoCard;
