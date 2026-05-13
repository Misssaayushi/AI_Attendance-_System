import React from 'react';
import { History, Trash2, UserCheck, UserMinus, UserX } from 'lucide-react';

const ActivityFeed = ({ logs, onClear }) => {
  const getStatusIcon = (status) => {
    switch (status) {
      case 'success': return <UserCheck size={14} className="text-green-500" />;
      case 'duplicate': return <UserMinus size={14} className="text-orange-500" />;
      case 'unknown': return <UserX size={14} className="text-red-500" />;
      default: return null;
    }
  };

  const getStatusBg = (status) => {
    switch (status) {
      case 'success': return 'bg-green-500/10 border-green-500/20';
      case 'duplicate': return 'bg-orange-500/10 border-orange-500/20';
      case 'unknown': return 'bg-red-500/10 border-red-500/20';
      default: return 'bg-gray-800/30 border-gray-700/30';
    }
  };

  return (
    <div className="flex flex-col h-full bg-gray-900/30 border border-gray-700/50 rounded-2xl overflow-hidden">
      <div className="p-4 border-b border-gray-700/50 flex items-center justify-between bg-gray-800/50">
        <h2 className="text-sm font-bold text-white flex items-center gap-2 uppercase tracking-widest">
          <History size={16} className="text-gray-400" />
          Recent Activity
        </h2>
        {logs.length > 0 && (
          <button 
            onClick={onClear}
            className="text-gray-500 hover:text-red-400 transition-colors"
            title="Clear Log"
          >
            <Trash2 size={14} />
          </button>
        )}
      </div>

      <div className="flex-1 overflow-y-auto p-4 space-y-3 custom-scrollbar">
        {logs.length === 0 ? (
          <div className="h-full flex flex-col items-center justify-center text-gray-600 space-y-2 opacity-50">
            <History size={32} />
            <p className="text-xs font-medium">No activity recorded yet</p>
          </div>
        ) : (
          logs.map((log) => (
            <div 
              key={log.id} 
              className={`flex items-center justify-between p-3 rounded-xl border transition-all animate-in slide-in-from-right-4 duration-300 ${getStatusBg(log.type)}`}
            >
              <div className="flex items-center gap-3">
                <div className="p-2 bg-gray-900/50 rounded-lg">
                  {getStatusIcon(log.type)}
                </div>
                <div>
                  <p className="text-xs font-bold text-white leading-none mb-1">{log.name}</p>
                  <p className="text-[10px] text-gray-500 uppercase font-medium">{log.message}</p>
                </div>
              </div>
              <span className="text-[10px] font-mono text-gray-500 whitespace-nowrap">{log.time}</span>
            </div>
          ))
        )}
      </div>

      <div className="p-3 bg-gray-800/20 border-t border-gray-700/30">
        <p className="text-[9px] text-center text-gray-600 uppercase font-bold tracking-widest">
          Auto-syncing with database
        </p>
      </div>
    </div>
  );
};

export default ActivityFeed;
