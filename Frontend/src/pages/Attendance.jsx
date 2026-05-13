import React, { useState, useEffect } from 'react';
import Container from '../components/Container';
import Card from '../components/Card';
import Button from '../components/Button';
import WebcamFeed from '../components/register/WebcamFeed';
import DetectionOverlay from '../components/attendance/DetectionOverlay';
import StatusPanel from '../components/attendance/StatusPanel';
import ActivityFeed from '../components/attendance/ActivityFeed';
import { Clock, Activity, Users, Zap } from 'lucide-react';

const Attendance = () => {
  const [isCameraActive, setIsCameraActive] = useState(false);
  const [recognitionState, setRecognitionState] = useState('idle');
  const [lastMatch, setLastMatch] = useState(null);
  const [logs, setLogs] = useState([
    { id: 1, name: 'Aman Verma', message: 'Already Marked', type: 'duplicate', time: '14:02:10' },
    { id: 2, name: 'Unknown Person', message: 'Recognition Failed', type: 'unknown', time: '13:58:45' }
  ]);
  const [time, setTime] = useState(new Date());

  useEffect(() => {
    const timer = setInterval(() => setTime(new Date()), 1000);
    return () => clearInterval(timer);
  }, []);

  const triggerSimulation = (type) => {
    setRecognitionState('scanning');
    
    setTimeout(() => {
      let logEntry = null;
      
      if (type === 'success') {
        const student = { name: 'Rahul Sharma', id: 'STU-2026-042' };
        setLastMatch(student);
        logEntry = { id: Date.now(), name: student.name, message: 'Attendance Marked', type: 'success', time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) };
      } else if (type === 'duplicate') {
        logEntry = { id: Date.now(), name: 'Aman Verma', message: 'Already Marked', type: 'duplicate', time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) };
      } else if (type === 'unknown') {
        logEntry = { id: Date.now(), name: 'Unknown Person', message: 'Recognition Failed', type: 'unknown', time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) };
      }

      setRecognitionState(type);
      if (logEntry) setLogs(prev => [logEntry, ...prev]);

      setTimeout(() => setRecognitionState('idle'), 4000);
    }, 1500);
  };

  return (
    <Container className="py-8 h-full flex flex-col">
      {/* Header */}
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center mb-8 gap-4">
        <div>
          <h1 className="text-3xl font-bold text-white flex items-center gap-3">
            <Zap className="text-blue-500 fill-blue-500/20" size={32} />
            Attendance Terminal
          </h1>
          <p className="text-gray-400 mt-1 font-medium italic">Scanning active... awaiting biometric input</p>
        </div>
        
        <div className="flex items-center space-x-6 bg-gray-900/80 backdrop-blur-xl px-6 py-3 rounded-2xl border border-gray-700/50 shadow-2xl">
          <div className="flex flex-col items-end">
            <span className="text-[10px] text-gray-500 uppercase font-black tracking-widest leading-none mb-1">Live Clock</span>
            <span className="text-xl font-mono text-blue-400 leading-none">{time.toLocaleTimeString()}</span>
          </div>
          <div className="h-8 w-px bg-gray-700"></div>
          <div className="flex flex-col items-start">
            <span className="text-[10px] text-gray-500 uppercase font-black tracking-widest leading-none mb-1">Network Status</span>
            <div className="flex items-center gap-2">
              <span className="w-2.5 h-2.5 rounded-full bg-green-500 animate-pulse shadow-[0_0_10px_rgba(34,197,94,0.5)]"></span>
              <span className="text-sm font-bold text-green-400 uppercase leading-none">Encrypted</span>
            </div>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 flex-1">
        {/* Left: Camera & Simulation (70%) */}
        <div className="lg:col-span-8 flex flex-col space-y-6">
          <div className="relative group rounded-3xl overflow-hidden border-2 border-gray-700/50 shadow-[0_0_40px_rgba(0,0,0,0.6)] bg-black">
            <WebcamFeed 
              onStreamStart={() => setIsCameraActive(true)}
              onStreamStop={() => {
                setIsCameraActive(false);
                setRecognitionState('idle');
              }}
            />
            {isCameraActive && (
              <DetectionOverlay isScanning={recognitionState === 'scanning'} />
            )}
          </div>

          <Card className="p-4 bg-gray-800/20 border-gray-700/30 flex flex-wrap items-center gap-4">
            <span className="text-xs font-bold text-gray-500 uppercase tracking-widest mr-2">Demo Simulation:</span>
            <Button 
              variant="secondary" size="sm" 
              onClick={() => triggerSimulation('success')}
              className="bg-green-500/10 border-green-500/20 text-green-400 hover:bg-green-500/20"
              disabled={recognitionState !== 'idle' || !isCameraActive}
            >
              Simulate Match
            </Button>
            <Button 
              variant="secondary" size="sm" 
              onClick={() => triggerSimulation('duplicate')}
              className="bg-orange-500/10 border-orange-500/20 text-orange-400 hover:bg-orange-500/20"
              disabled={recognitionState !== 'idle' || !isCameraActive}
            >
              Simulate Duplicate
            </Button>
            <Button 
              variant="secondary" size="sm" 
              onClick={() => triggerSimulation('unknown')}
              className="bg-red-500/10 border-red-500/20 text-red-400 hover:bg-red-500/20"
              disabled={recognitionState !== 'idle' || !isCameraActive}
            >
              Simulate Unknown
            </Button>
          </Card>
        </div>

        {/* Right: Sidebar (30%) */}
        <div className="lg:col-span-4 flex flex-col h-full space-y-6">
          <StatusPanel state={recognitionState} student={lastMatch} />

          {/* Stats */}
          <div className="grid grid-cols-2 gap-4">
            <Card className="p-4 bg-blue-600/5 border-blue-600/20 flex flex-col items-center">
              <span className="text-[9px] text-blue-400 font-black tracking-tighter uppercase mb-1">Present Today</span>
              <div className="flex items-center gap-2">
                <Users size={14} className="text-blue-500" />
                <span className="text-2xl font-bold text-white tracking-tighter">{42 + logs.filter(l => l.type === 'success').length}</span>
              </div>
            </Card>
            <Card className="p-4 bg-violet-600/5 border-violet-600/20 flex flex-col items-center">
              <span className="text-[9px] text-violet-400 font-black tracking-tighter uppercase mb-1">Percentage</span>
              <div className="flex items-center gap-2">
                <Activity size={14} className="text-violet-500" />
                <span className="text-2xl font-bold text-white tracking-tighter">31%</span>
              </div>
            </Card>
          </div>

          <ActivityFeed logs={logs} onClear={() => setLogs([])} />
        </div>
      </div>
    </Container>
  );
};

export default Attendance;
