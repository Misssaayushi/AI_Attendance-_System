import React from 'react';
import Card from '../Card';

const StatCard = ({ title, value, icon, trend, trendType = 'neutral', color = 'blue' }) => {
  const colorConfigs = {
    blue: {
      border: 'border-blue-500/30',
      iconBg: 'bg-blue-500/10 text-blue-400 border border-blue-500/20',
      glow: 'shadow-blue-500/5 hover:shadow-blue-500/10',
      gradient: 'from-blue-500/5 to-transparent',
      textAccent: 'text-blue-400'
    },
    green: {
      border: 'border-green-500/30',
      iconBg: 'bg-green-500/10 text-green-400 border border-green-500/20',
      glow: 'shadow-green-500/5 hover:shadow-green-500/10',
      gradient: 'from-green-500/5 to-transparent',
      textAccent: 'text-green-400'
    },
    red: {
      border: 'border-red-500/30',
      iconBg: 'bg-red-500/10 text-red-400 border border-red-500/20',
      glow: 'shadow-red-500/5 hover:shadow-red-500/10',
      gradient: 'from-red-500/5 to-transparent',
      textAccent: 'text-red-400'
    },
    purple: {
      border: 'border-purple-500/30',
      iconBg: 'bg-purple-500/10 text-purple-400 border border-purple-500/20',
      glow: 'shadow-purple-500/5 hover:shadow-purple-500/10',
      gradient: 'from-purple-500/5 to-transparent',
      textAccent: 'text-purple-400'
    }
  };

  const current = colorConfigs[color] || colorConfigs.blue;

  const getTrendColor = () => {
    if (trendType === 'up') return 'text-green-400 bg-green-500/10 border border-green-500/20';
    if (trendType === 'down') return 'text-red-400 bg-red-500/10 border border-red-500/20';
    return 'text-gray-400 bg-gray-800/80 border border-gray-700/30';
  };

  return (
    <Card className={`relative overflow-hidden p-6 transition-all duration-350 hover:scale-[1.03] hover:-translate-y-1 shadow-2xl border ${current.border} ${current.glow} bg-gradient-to-br ${current.gradient} flex items-center justify-between group`}>
      {/* Decorative subtle background mesh glow */}
      <div className={`absolute -right-10 -bottom-10 w-32 h-32 rounded-full blur-3xl opacity-20 transition-opacity duration-300 group-hover:opacity-30 bg-current`} style={{ color: color === 'blue' ? '#3b82f6' : color === 'green' ? '#22c55e' : color === 'red' ? '#ef4444' : '#a855f7' }} />
      
      <div className="space-y-2.5 z-10">
        <p className="text-[10px] text-gray-400 font-black uppercase tracking-widest">{title}</p>
        <p className="text-3xl font-black text-white tracking-tight font-sans bg-clip-text">
          {value}
        </p>
        {trend && (
          <span className={`inline-flex items-center px-2 py-0.5 rounded-lg text-[9px] font-black uppercase tracking-wider ${getTrendColor()}`}>
            {trend}
          </span>
        )}
      </div>
      <div className={`p-4 rounded-2xl ${current.iconBg} shadow-inner transition-transform duration-300 group-hover:rotate-6 group-hover:scale-110 z-10`}>
        {icon}
      </div>
    </Card>
  );
};

export default StatCard;
