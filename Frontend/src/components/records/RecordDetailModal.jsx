import React from 'react';
import { X, Calendar, Clock, Award, ShieldAlert } from 'lucide-react';
import Card from '../Card';

const RecordDetailModal = ({ record, onClose }) => {
  if (!record) return null;

  // Generate some realistic detailed logs for the selected student
  const detailLogs = [
    { date: '2026-05-13', time: record.time, status: record.status, confidence: '94.8%', device: 'Entrance Camera #1' },
    { date: '2026-05-12', time: '09:02 AM', status: 'Present', confidence: '96.1%', device: 'Entrance Camera #1' },
    { date: '2026-05-11', time: '09:14 AM', status: 'Late', confidence: '92.4%', device: 'Lab Terminal #3' },
    { date: '2026-05-10', time: '---', status: 'Absent', confidence: '0.0%', device: 'System Scheduler' },
    { date: '2026-05-09', time: '08:58 AM', status: 'Present', confidence: '97.5%', device: 'Entrance Camera #1' },
  ];

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
      {/* Backdrop */}
      <div 
        className="fixed inset-0 bg-black/80 backdrop-blur-sm transition-opacity"
        onClick={onClose}
      />

      {/* Modal Content */}
      <Card className="relative w-full max-w-lg bg-gray-900 border border-gray-800/80 shadow-2xl overflow-hidden rounded-2xl z-10 animate-in fade-in zoom-in-95 duration-200">
        {/* Header */}
        <div className="p-5 border-b border-gray-800/80 flex items-center justify-between bg-gray-950/40">
          <div>
            <h3 className="text-base font-bold text-white uppercase tracking-wider">Verification Audit Log</h3>
            <p className="text-[10px] text-gray-500 mt-0.5">Biometric logs and matching telemetry</p>
          </div>
          <button 
            onClick={onClose}
            className="p-1.5 rounded-lg bg-gray-800/50 hover:bg-gray-800 text-gray-400 hover:text-white transition-colors"
          >
            <X size={16} />
          </button>
        </div>

        {/* Body */}
        <div className="p-6 space-y-6">
          {/* Student Profile Snapshot */}
          <div className="flex items-center space-x-4 bg-gray-850/30 p-4 rounded-xl border border-gray-800/50">
            <div className="w-12 h-12 rounded-xl bg-blue-500/10 border border-blue-500/20 flex items-center justify-center text-blue-400 font-extrabold text-lg">
              {record.name.split(' ').map(n => n[0]).join('')}
            </div>
            <div>
              <h4 className="text-sm font-bold text-white leading-none mb-1.5">{record.name}</h4>
              <div className="flex flex-wrap gap-2 items-center">
                <span className="text-[10px] font-mono text-gray-400 uppercase bg-gray-800/80 border border-gray-700/50 px-1.5 py-0.5 rounded">
                  {record.id}
                </span>
                <span className="text-[10px] font-bold text-gray-400 bg-gray-800/80 border border-gray-700/50 px-1.5 py-0.5 rounded">
                  Dept: {record.department}
                </span>
              </div>
            </div>
          </div>

          {/* Quick Metrics */}
          <div className="grid grid-cols-2 gap-4">
            <div className="bg-gray-850/20 p-4 rounded-xl border border-gray-800/30 text-center">
              <p className="text-[10px] text-gray-500 font-bold uppercase tracking-wider">Overall Rate</p>
              <p className="text-xl font-black text-blue-400 font-mono mt-1">88.4%</p>
            </div>
            <div className="bg-gray-850/20 p-4 rounded-xl border border-gray-800/30 text-center">
              <p className="text-[10px] text-gray-500 font-bold uppercase tracking-wider">Last Match</p>
              <p className="text-xl font-black text-green-400 font-mono mt-1">
                {record.status === 'Absent' ? 'N/A' : '94.8%'}
              </p>
            </div>
          </div>

          {/* Timeline Logs */}
          <div className="space-y-3">
            <h5 className="text-[10px] text-gray-500 font-black uppercase tracking-wider">Verification History (Last 5 Days)</h5>
            <div className="space-y-2 max-h-[180px] overflow-y-auto pr-1 custom-scrollbar">
              {detailLogs.map((log, i) => (
                <div 
                  key={i} 
                  className="flex items-center justify-between p-3 bg-gray-850/10 hover:bg-gray-850/25 border border-gray-800/30 rounded-xl text-xs transition-colors"
                >
                  <div className="flex items-center space-x-3">
                    <Calendar size={14} className="text-gray-500" />
                    <div>
                      <p className="font-bold text-white">{log.date}</p>
                      <p className="text-[9px] text-gray-500 mt-0.5">{log.device}</p>
                    </div>
                  </div>
                  <div className="text-right">
                    <div className="flex items-center justify-end space-x-1.5">
                      <Clock size={12} className="text-gray-500" />
                      <span className="font-mono font-medium text-gray-300">{log.time}</span>
                    </div>
                    <div className="mt-1 flex items-center justify-end space-x-1.5">
                      <span className={`text-[9px] font-black uppercase ${
                        log.status === 'Present' ? 'text-green-400' :
                        log.status === 'Late' ? 'text-orange-400' : 'text-red-400'
                      }`}>
                        {log.status}
                      </span>
                      {log.status !== 'Absent' && (
                        <span className="text-[9px] text-gray-500 font-mono">({log.confidence})</span>
                      )}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Footer */}
        <div className="p-4 border-t border-gray-800/80 bg-gray-950/20 text-right">
          <button 
            onClick={onClose}
            className="px-4 py-2 bg-gray-800 hover:bg-gray-750 text-white rounded-xl text-xs font-bold transition-all"
          >
            Close Audit
          </button>
        </div>
      </Card>
    </div>
  );
};

export default RecordDetailModal;
